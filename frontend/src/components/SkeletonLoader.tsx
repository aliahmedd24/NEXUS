interface Props {
  width?: string | number;
  height?: string | number;
  count?: number;
  gap?: number;
}

export function SkeletonLoader({ width = '100%', height = 20, count = 1, gap = 8 }: Props) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap }}>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="skeleton" style={{ width, height, borderRadius: 6 }} />
      ))}
    </div>
  );
}
