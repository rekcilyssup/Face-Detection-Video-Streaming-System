import type { ConnectionState } from '../types';

interface HeaderProps {
  connectionState: ConnectionState;
}

const STATUS_CONFIG: Record<ConnectionState, { label: string; dotClass: string }> = {
  connected: { label: 'Connected', dotClass: 'animate-pulse-secondary bg-secondary' },
  connecting: { label: 'Connecting…', dotClass: 'animate-pulse-secondary bg-tertiary' },
  disconnected: { label: 'Disconnected', dotClass: 'bg-outline-variant' },
  error: { label: 'Connection Error', dotClass: 'animate-pulse-error' },
};

export default function Header({ connectionState }: HeaderProps) {
  const status = STATUS_CONFIG[connectionState];

  return (
    <header className="flex justify-between items-center h-12 px-lg w-full z-50 border-b border-outline-variant/30 bg-surface">
      <div className="flex items-center gap-md">
        <span className="text-h2 font-h2 font-black tracking-tight text-primary">
          FaceStream
        </span>
      </div>
      <div className="flex-1 flex justify-center">
        <div className="flex items-center gap-xs px-md py-xs rounded-full border-thin bg-surface-container">
          <span className={status.dotClass}></span>
          <span className="font-body-sm text-body-sm text-on-surface-variant">
            {status.label}
          </span>
        </div>
      </div>
      <div className="flex items-center gap-lg">
        <nav className="hidden md:flex gap-lg">
          <span className="text-primary font-bold border-b-2 border-primary pb-1 cursor-default">
            Dashboard
          </span>
        </nav>
      </div>
    </header>
  );
}
