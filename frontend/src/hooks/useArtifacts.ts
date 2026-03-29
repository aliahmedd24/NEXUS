import { useState, useRef, useCallback } from 'react';
import { type Mode } from '../types/api';
import { type ArtifactItem, type ArtifactGroup, VIZ_TYPE_LABELS } from '../types/artifacts';

export function useArtifacts() {
  const [groups, setGroups] = useState<ArtifactGroup[]>([]);
  const currentGroupRef = useRef<ArtifactGroup | null>(null);

  /** Called when the user sends a message — opens a new artifact group. */
  const startGroup = useCallback((mode: Mode, userQuery: string) => {
    currentGroupRef.current = {
      id: crypto.randomUUID(),
      mode,
      userQuery,
      items: [],
      agentName: '',
      completedAt: null,
      createdAt: Date.now(),
    };
  }, []);

  /** Called on each visualization SSE event — appends an item to the current group. */
  const addItem = useCallback((vizType: string, toolName: string, data: unknown) => {
    if (!currentGroupRef.current) return;
    const item: ArtifactItem = {
      id: crypto.randomUUID(),
      vizType,
      toolName,
      data,
      timestamp: Date.now(),
      label: VIZ_TYPE_LABELS[vizType] || vizType,
    };
    currentGroupRef.current.items.push(item);
  }, []);

  /** Called on the "done" SSE event — finalizes the group and pushes to state. */
  const finalizeGroup = useCallback((agentName: string) => {
    const group = currentGroupRef.current;
    if (!group || group.items.length === 0) {
      // Discard empty groups (no tool results = no artifacts)
      currentGroupRef.current = null;
      return;
    }
    group.agentName = agentName;
    group.completedAt = Date.now();
    setGroups(prev => [group, ...prev]); // newest first
    currentGroupRef.current = null;
  }, []);

  const removeGroup = useCallback((groupId: string) => {
    setGroups(prev => prev.filter(g => g.id !== groupId));
  }, []);

  const clearAll = useCallback(() => {
    setGroups([]);
  }, []);

  return { groups, startGroup, addItem, finalizeGroup, removeGroup, clearAll };
}
