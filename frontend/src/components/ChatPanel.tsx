import { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '../lib/api';
import { type Mode } from '../types/api';

interface ChatMessage {
  id: string;
  role: 'user' | 'agent' | 'system';
  agent?: string;
  text: string;
  toolCalls?: { tool: string; args: Record<string, unknown> }[];
  thinking?: string;
  isStreaming?: boolean;
  timestamp: number;
}

interface Props {
  mode: Mode;
  open: boolean;
  onToggle: () => void;
  onVisualization?: (type: string, data: unknown, toolName?: string) => void;
  onStreamStart?: (userQuery: string) => void;
  onStreamDone?: (agentName: string) => void;
}

const modeAgentNames: Record<Mode, string> = {
  diagnose: 'Vulnerability Scanner',
  staff: 'Talent Intelligence',
  learn: 'Decision Replay',
};

const modeColors: Record<Mode, string> = {
  diagnose: '#ef4444',
  staff: '#1e88e5',
  learn: '#a78bfa',
};

const modeSuggestions: Record<Mode, string[]> = {
  diagnose: [
    'Run a stress test for the Battery Supply Chain Crisis scenario',
    'What are our biggest leadership vulnerabilities right now?',
    'Create a compound scenario combining EV Transformation and Trade War',
  ],
  staff: [
    'Find the best candidates for the Plant Director role',
    'Who should we hire for Head of EV Battery Systems under the Neue Klasse scenario?',
    'Compare internal vs external candidates for CTO',
  ],
  learn: [
    'Replay our past hiring decisions and find patterns',
    'What biases exist in our historical leadership decisions?',
    'Run the full learn pipeline and update calibration',
  ],
};

export function ChatPanel({ mode, open, onToggle, onVisualization, onStreamStart, onStreamDone }: Props) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [streaming, setStreaming] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [activeAgent, setActiveAgent] = useState<string | null>(null);
  const [activeTools, setActiveTools] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  // Ref to track the streaming message id — updated without re-renders
  const streamMsgIdRef = useRef<string | null>(null);
  // Track the last agent name seen — used for artifact finalization after stream ends
  const lastAgentRef = useRef<string>('agent');

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, activeTools]);

  // Focus input when panel opens
  useEffect(() => {
    if (open) setTimeout(() => inputRef.current?.focus(), 300);
  }, [open]);

  // Create session on first open
  useEffect(() => {
    if (open && !sessionId) {
      api.createSession().then(res => setSessionId(res.session_id)).catch(console.error);
    }
  }, [open, sessionId]);

  /**
   * Ensure a streaming agent message exists in the messages array.
   * If one doesn't exist yet, create it. Returns the message id.
   */
  const ensureStreamMsg = useCallback((agent: string): string => {
    if (streamMsgIdRef.current) return streamMsgIdRef.current;
    const id = crypto.randomUUID();
    streamMsgIdRef.current = id;
    setMessages(prev => [...prev, {
      id,
      role: 'agent',
      agent,
      text: '',
      toolCalls: [],
      thinking: '',
      isStreaming: true,
      timestamp: Date.now(),
    }]);
    return id;
  }, []);

  /**
   * Update a field on the streaming message by id.
   */
  const updateStreamMsg = useCallback((id: string, updater: (msg: ChatMessage) => ChatMessage) => {
    setMessages(prev => prev.map(m => m.id === id ? updater(m) : m));
  }, []);

  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim() || streaming) return;

    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      text: text.trim(),
      timestamp: Date.now(),
    };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setStreaming(true);
    setActiveTools([]);
    streamMsgIdRef.current = null;
    lastAgentRef.current = 'agent';
    onStreamStart?.(text.trim());

    // Ensure we have a session
    let sid = sessionId;
    if (!sid) {
      try {
        const res = await api.createSession();
        sid = res.session_id;
        setSessionId(sid);
      } catch {
        setMessages(prev => [...prev, {
          id: crypto.randomUUID(),
          role: 'system',
          text: 'Failed to create session. Is the backend running?',
          timestamp: Date.now(),
        }]);
        setStreaming(false);
        return;
      }
    }

    try {
      const response = await api.sendMessage(text.trim(), sid, mode);
      if (!response.body) throw new Error('No response body');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      const processEvent = (eventType: string, rawData: string) => {
        const trimmed = rawData.trim();
        if (!trimmed) return;
        let data: Record<string, unknown>;
        try {
          data = JSON.parse(trimmed);
        } catch (e) {
          console.warn('[NEXUS SSE] parse error:', trimmed.slice(0, 80), e);
          return;
        }
        console.log(`[NEXUS SSE] ${eventType}`, data);

        const agent = (data.agent as string) || 'agent';

        switch (eventType) {
          case 'thinking': {
            const id = ensureStreamMsg(agent);
            updateStreamMsg(id, msg => ({
              ...msg,
              agent,
              thinking: (msg.thinking || '') + (data.text as string) + '\n',
            }));
            setActiveAgent(agent);
            break;
          }
          case 'tool_call': {
            const id = ensureStreamMsg(agent);
            updateStreamMsg(id, msg => ({
              ...msg,
              agent,
              toolCalls: [...(msg.toolCalls || []), { tool: data.tool as string, args: (data.args || {}) as Record<string, unknown> }],
            }));
            setActiveTools(prev => [...prev, data.tool as string]);
            setActiveAgent(agent);
            break;
          }
          case 'tool_result': {
            setActiveTools(prev => prev.filter((_, i) => i !== 0));
            break;
          }
          case 'text': {
            if (data.text) {
              const id = ensureStreamMsg(agent);
              updateStreamMsg(id, msg => ({
                ...msg,
                agent,
                text: msg.text + (data.text as string),
              }));
              setActiveAgent(agent);
            }
            break;
          }
          case 'done': {
            // ADK emits `is_final_response()` for EACH sub-agent in a
            // SequentialAgent pipeline. We must NOT finalize artifacts here
            // because later sub-agents may still emit visualization events.
            // Instead, track the agent name and finalize after the stream ends.
            lastAgentRef.current = (data.agent as string) || 'agent';

            // Finalize the current streaming message bubble (UI only)
            if (streamMsgIdRef.current) {
              updateStreamMsg(streamMsgIdRef.current, msg => ({
                ...msg,
                isStreaming: false,
                thinking: msg.thinking?.trim() || undefined,
              }));
            }
            // Reset for next sub-agent's message bubble
            streamMsgIdRef.current = null;
            setActiveAgent(null);
            setActiveTools([]);
            break;
          }
          case 'visualization': {
            console.log(`[NEXUS VIZ] ${data.type}`, data.data);
            onVisualization?.(data.type as string, data.data, data.tool as string);
            break;
          }
          case 'error': {
            setMessages(prev => [...prev, {
              id: crypto.randomUUID(),
              role: 'system',
              text: `Error: ${data.message}`,
              timestamp: Date.now(),
            }]);
            break;
          }
        }
      };

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // Parse SSE blocks: split on double-newline
        const blocks = buffer.split(/\r?\n\r?\n/);
        buffer = blocks.pop() || '';

        for (const block of blocks) {
          if (!block.trim()) continue;
          const lines = block.split(/\r?\n/);
          let evType = 'message';
          const dataLines: string[] = [];
          for (const line of lines) {
            if (line.startsWith('event:')) {
              evType = line.slice(6).trim();
            } else if (line.startsWith('data:')) {
              dataLines.push(line.slice(5).trimStart());
            }
          }
          if (dataLines.length > 0) {
            processEvent(evType, dataLines.join('\n'));
          }
        }
      }

      // Process any remaining buffer
      if (buffer.trim()) {
        const lines = buffer.split(/\r?\n/);
        let evType = 'message';
        const dataLines: string[] = [];
        for (const line of lines) {
          if (line.startsWith('event:')) {
            evType = line.slice(6).trim();
          } else if (line.startsWith('data:')) {
            dataLines.push(line.slice(5).trimStart());
          }
        }
        if (dataLines.length > 0) {
          processEvent(evType, dataLines.join('\n'));
        }
      }

      // If stream ended without a done event, finalize the streaming message
      if (streamMsgIdRef.current) {
        updateStreamMsg(streamMsgIdRef.current, msg => ({
          ...msg,
          isStreaming: false,
          thinking: msg.thinking?.trim() || undefined,
        }));
        streamMsgIdRef.current = null;
      }

      // Finalize artifact group now that the ENTIRE stream is complete.
      // This runs after ALL sub-agents have finished, so all visualization
      // events have been collected into the artifact group.
      onStreamDone?.(lastAgentRef.current);
    } catch (e) {
      setMessages(prev => [...prev, {
        id: crypto.randomUUID(),
        role: 'system',
        text: `Connection error: ${e instanceof Error ? e.message : 'Unknown error'}`,
        timestamp: Date.now(),
      }]);
      // Still finalize artifacts on error — partial results are still useful
      onStreamDone?.(lastAgentRef.current);
    } finally {
      setStreaming(false);
      setActiveAgent(null);
      setActiveTools([]);
      streamMsgIdRef.current = null;
    }
  }, [sessionId, streaming, mode, ensureStreamMsg, updateStreamMsg, onVisualization, onStreamStart, onStreamDone]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  const accentColor = modeColors[mode];

  return (
    <>
      {/* Toggle Button */}
      <button
        onClick={onToggle}
        style={{
          position: 'fixed',
          bottom: 48,
          right: 20,
          zIndex: 1000,
          width: 48,
          height: 48,
          borderRadius: '50%',
          border: `2px solid ${accentColor}`,
          background: open ? accentColor : 'rgba(10,15,26,0.95)',
          color: open ? '#fff' : accentColor,
          fontSize: 20,
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: `0 0 20px ${accentColor}33`,
          transition: 'all 200ms',
        }}
        title={open ? 'Close chat' : `Chat with ${modeAgentNames[mode]}`}
      >
        {open ? '\u2715' : '\u2726'}
      </button>

      {/* Chat Panel */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ x: 420, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 420, opacity: 0 }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            style={{
              position: 'fixed',
              top: 0,
              right: 0,
              bottom: 0,
              width: 400,
              zIndex: 999,
              display: 'flex',
              flexDirection: 'column',
              background: 'rgba(10,15,26,0.97)',
              borderLeft: `1px solid ${accentColor}33`,
              backdropFilter: 'blur(20px)',
            }}
          >
            {/* Header */}
            <div style={{
              padding: '16px 20px',
              borderBottom: '1px solid rgba(255,255,255,0.06)',
              display: 'flex',
              alignItems: 'center',
              gap: 10,
              flexShrink: 0,
            }}>
              <div style={{
                width: 8, height: 8, borderRadius: '50%',
                background: accentColor,
                boxShadow: `0 0 8px ${accentColor}`,
              }} />
              <div>
                <div style={{
                  font: '600 14px/1 var(--font-display)',
                  color: '#f1f5f9',
                  letterSpacing: '0.04em',
                }}>
                  {modeAgentNames[mode]}
                </div>
                <div style={{
                  font: '400 11px/1.2 var(--font-body)',
                  color: '#64748b',
                  marginTop: 2,
                }}>
                  NEXUS Agent &middot; {mode.toUpperCase()} mode
                </div>
              </div>
              {streaming && (
                <div style={{
                  marginLeft: 'auto',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,
                }}>
                  <span className="pulse-dot" style={{ width: 6, height: 6, borderRadius: '50%', background: accentColor }} />
                  <span style={{ font: '400 11px/1 var(--font-body)', color: accentColor }}>
                    {activeAgent || 'thinking'}...
                  </span>
                </div>
              )}
            </div>

            {/* Messages */}
            <div style={{
              flex: 1,
              overflow: 'auto',
              padding: '16px 16px 8px',
              display: 'flex',
              flexDirection: 'column',
              gap: 12,
            }}>
              {/* Welcome + Suggestions */}
              {messages.length === 0 && !streaming && (
                <div style={{ padding: '20px 0' }}>
                  <div style={{
                    font: '500 13px/1.4 var(--font-body)',
                    color: '#94a3b8',
                    marginBottom: 16,
                  }}>
                    Ask me anything about {mode === 'diagnose' ? 'organizational vulnerabilities' : mode === 'staff' ? 'talent and staffing' : 'past decisions and biases'}.
                    I'll use NEXUS tools to analyze your data.
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                    {modeSuggestions[mode].map((s, i) => (
                      <button
                        key={i}
                        onClick={() => sendMessage(s)}
                        style={{
                          font: '400 12px/1.4 var(--font-body)',
                          padding: '8px 12px',
                          borderRadius: 8,
                          border: '1px solid rgba(255,255,255,0.06)',
                          background: 'rgba(255,255,255,0.02)',
                          color: '#94a3b8',
                          cursor: 'pointer',
                          textAlign: 'left',
                          transition: 'all 150ms',
                        }}
                        onMouseEnter={e => {
                          e.currentTarget.style.borderColor = `${accentColor}44`;
                          e.currentTarget.style.color = '#f1f5f9';
                        }}
                        onMouseLeave={e => {
                          e.currentTarget.style.borderColor = 'rgba(255,255,255,0.06)';
                          e.currentTarget.style.color = '#94a3b8';
                        }}
                      >
                        {s}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* All messages — including the streaming one */}
              {messages.map(msg => (
                <MessageBubble key={msg.id} message={msg} accentColor={accentColor} activeTools={msg.isStreaming ? activeTools : []} />
              ))}

              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div style={{
              padding: '12px 16px 16px',
              borderTop: '1px solid rgba(255,255,255,0.06)',
              flexShrink: 0,
            }}>
              <div style={{
                display: 'flex',
                gap: 8,
                alignItems: 'flex-end',
              }}>
                <textarea
                  ref={inputRef}
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder={streaming ? 'Agent is thinking...' : 'Ask NEXUS...'}
                  disabled={streaming}
                  rows={1}
                  style={{
                    flex: 1,
                    font: '400 13px/1.5 var(--font-body)',
                    padding: '10px 12px',
                    borderRadius: 8,
                    border: '1px solid rgba(255,255,255,0.1)',
                    background: '#1a2236',
                    color: '#f1f5f9',
                    outline: 'none',
                    resize: 'none',
                    maxHeight: 120,
                    minHeight: 40,
                  }}
                  onInput={e => {
                    const el = e.currentTarget;
                    el.style.height = 'auto';
                    el.style.height = Math.min(el.scrollHeight, 120) + 'px';
                  }}
                />
                <button
                  onClick={() => sendMessage(input)}
                  disabled={!input.trim() || streaming}
                  style={{
                    width: 40,
                    height: 40,
                    borderRadius: 8,
                    border: 'none',
                    background: input.trim() && !streaming ? accentColor : 'rgba(255,255,255,0.06)',
                    color: input.trim() && !streaming ? '#fff' : '#64748b',
                    fontSize: 16,
                    cursor: input.trim() && !streaming ? 'pointer' : 'not-allowed',
                    flexShrink: 0,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    transition: 'all 150ms',
                  }}
                >
                  &#9654;
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}

function MessageBubble({ message, accentColor, activeTools = [] }: { message: ChatMessage; accentColor: string; activeTools?: string[] }) {
  const [showThinking, setShowThinking] = useState(false);
  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';

  return (
    <div style={{
      alignSelf: isUser ? 'flex-end' : 'flex-start',
      maxWidth: '92%',
    }}>
      {/* Agent label */}
      {!isUser && message.agent && (
        <div style={{
          font: '500 10px/1 var(--font-mono)',
          color: isSystem ? '#f59e0b' : accentColor,
          marginBottom: 4,
          letterSpacing: '0.06em',
          textTransform: 'uppercase',
        }}>
          {message.agent}
        </div>
      )}

      {/* Tool calls summary */}
      {message.toolCalls && message.toolCalls.length > 0 && (
        <div style={{
          marginBottom: 6,
          padding: '6px 10px',
          borderRadius: 6,
          background: 'rgba(255,255,255,0.02)',
          border: '1px solid rgba(255,255,255,0.04)',
          display: 'flex',
          flexDirection: 'column',
          gap: 2,
        }}>
          {message.toolCalls.map((tc, i) => (
            <div key={i} style={{
              font: '400 11px/1.3 var(--font-mono)',
              color: '#64748b',
            }}>
              <span style={{ color: accentColor }}>{tc.tool}</span>
              ({Object.entries(tc.args).map(([k, v]) => `${k}=${JSON.stringify(v)}`).join(', ')})
            </div>
          ))}
        </div>
      )}

      {/* Active tool spinners */}
      {activeTools.length > 0 && (
        <div style={{
          padding: '8px 12px',
          borderRadius: 8,
          border: `1px solid ${accentColor}22`,
          background: `${accentColor}08`,
          display: 'flex',
          flexDirection: 'column',
          gap: 4,
          marginBottom: 6,
        }}>
          {activeTools.map((tool, i) => (
            <div key={i} style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              font: '500 11px/1 var(--font-mono)',
              color: accentColor,
            }}>
              <span style={{
                display: 'inline-block',
                width: 12, height: 12,
                border: `2px solid ${accentColor}33`,
                borderTop: `2px solid ${accentColor}`,
                borderRadius: '50%',
                animation: 'spin 1s linear infinite',
              }} />
              {tool}()
            </div>
          ))}
        </div>
      )}

      {/* Thinking toggle */}
      {message.thinking && message.thinking.trim() && (
        <button
          onClick={() => setShowThinking(!showThinking)}
          style={{
            font: '400 10px/1 var(--font-body)',
            color: '#64748b',
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            padding: '2px 0',
            marginBottom: 4,
          }}
        >
          {showThinking ? '\u25BC' : '\u25B6'} thinking ({message.thinking.trim().split('\n').length} steps)
        </button>
      )}
      {showThinking && message.thinking && (
        <div style={{
          font: '400 11px/1.4 var(--font-mono)',
          color: '#475569',
          padding: '6px 10px',
          borderRadius: 6,
          background: 'rgba(255,255,255,0.02)',
          marginBottom: 6,
          maxHeight: 200,
          overflow: 'auto',
          whiteSpace: 'pre-wrap',
        }}>
          {message.thinking}
        </div>
      )}

      {/* Message text bubble */}
      {(message.text || message.isStreaming) && (
        <div style={{
          padding: '10px 14px',
          borderRadius: isUser ? '12px 12px 2px 12px' : '12px 12px 12px 2px',
          background: isUser
            ? `${accentColor}18`
            : isSystem
            ? 'rgba(245,158,11,0.08)'
            : 'rgba(255,255,255,0.04)',
          border: `1px solid ${isUser ? `${accentColor}33` : isSystem ? 'rgba(245,158,11,0.2)' : 'rgba(255,255,255,0.06)'}`,
          font: '400 13px/1.6 var(--font-body)',
          color: isSystem ? '#f59e0b' : '#e2e8f0',
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word',
          minHeight: message.isStreaming && !message.text ? 20 : undefined,
        }}>
          {message.text}
          {message.isStreaming && (
            <span className="pulse-dot" style={{
              display: 'inline-block',
              width: 6,
              height: 6,
              borderRadius: '50%',
              background: accentColor,
              marginLeft: 4,
              verticalAlign: 'middle',
            }} />
          )}
        </div>
      )}
    </div>
  );
}
