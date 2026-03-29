interface Props {
  icon?: string;
  title: string;
  description: string;
  action?: { label: string; onClick: () => void };
}

export function EmptyState({ icon = '◇', title, description, action }: Props) {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: 48,
      border: '1px solid rgba(255,255,255,0.06)',
      borderRadius: 10,
      textAlign: 'center',
      gap: 12,
    }}>
      <span style={{ fontSize: 32, color: '#64748b' }}>{icon}</span>
      <span className="text-heading" style={{ color: '#f1f5f9' }}>{title}</span>
      <span className="text-body-sm" style={{ color: '#94a3b8', maxWidth: 320 }}>{description}</span>
      {action && (
        <button
          onClick={action.onClick}
          style={{
            marginTop: 8,
            font: '500 13px/1 var(--font-body)',
            padding: '8px 16px',
            borderRadius: 6,
            border: '1px solid rgba(30,136,229,0.4)',
            background: 'rgba(30,136,229,0.1)',
            color: '#1e88e5',
            cursor: 'pointer',
          }}
        >
          {action.label} →
        </button>
      )}
    </div>
  );
}
