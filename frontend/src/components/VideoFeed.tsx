import { RefObject } from 'react';
import { Video, VideoOff } from 'lucide-react';
import type { ConnectionState } from '../types';

interface VideoFeedProps {
  currentFrame: string | null;
  fps: number;
  isStreaming: boolean;
  connectionState: ConnectionState;
  webcamRef: RefObject<HTMLVideoElement | null>;
  onToggleStream: () => void;
  error: string | null;
}

export default function VideoFeed({
  currentFrame,
  fps,
  isStreaming,
  connectionState,
  webcamRef,
  onToggleStream,
  error,
}: VideoFeedProps) {
  return (
    <section id="video-feed" className="w-full lg:w-[65%] flex flex-col">
      <div className="card-surface border-thin flex-1 flex flex-col relative rounded-none overflow-hidden h-full min-h-[300px]">
        {/* Stream Overlay — Top */}
        <div className="absolute top-0 left-0 w-full p-sm flex justify-between items-start z-10">
          <div className="flex items-center gap-xs bg-surface-container/80 backdrop-blur-sm px-sm py-xs border-thin">
            {isStreaming ? (
              <>
                <span className="animate-pulse-error"></span>
                <span className="font-label-caps text-label-caps text-error">LIVE</span>
              </>
            ) : (
              <span className="font-label-caps text-label-caps text-outline-variant">OFFLINE</span>
            )}
          </div>
          <div className="bg-surface-container/80 backdrop-blur-sm px-sm py-xs border-thin">
            <span className="font-data-mono text-data-mono text-primary">CAM_01_MAIN</span>
          </div>
        </div>

        {/* Video Area */}
        <div className="flex-1 w-full bg-black relative flex items-center justify-center overflow-hidden">
          {/* Hidden video element used by webcam capture hook */}
          <video ref={webcamRef} className="hidden" playsInline muted />

          {currentFrame ? (
            <img
              src={currentFrame}
              alt="Annotated stream with face detection"
              className="w-full h-full object-contain"
            />
          ) : (
            <div className="flex flex-col items-center gap-md text-outline-variant">
              {error ? (
                <>
                  <VideoOff size={48} className="text-error" />
                  <span className="font-body-base text-error text-center px-lg">{error}</span>
                </>
              ) : (
                <>
                  <Video size={48} />
                  <span className="font-body-base text-center">
                    {connectionState === 'connecting'
                      ? 'Connecting to stream…'
                      : 'Click "Start Stream" to begin face detection'}
                  </span>
                </>
              )}
            </div>
          )}
        </div>

        {/* Stream Overlay — Bottom */}
        <div className="absolute bottom-0 left-0 w-full p-sm flex justify-between items-end z-10">
          <div className="bg-surface-container/80 backdrop-blur-sm px-sm py-xs border-thin">
            <span className="font-data-mono text-data-mono text-outline-variant">
              {isStreaming ? `${fps} fps` : '-- fps'} | 640×480
            </span>
          </div>
          <button
            id="toggle-stream-btn"
            onClick={onToggleStream}
            className={`flex items-center gap-xs px-md py-xs border-thin font-label-caps text-label-caps transition-colors cursor-pointer ${
              isStreaming
                ? 'bg-error/20 text-error hover:bg-error/30'
                : 'bg-secondary/20 text-secondary hover:bg-secondary/30'
            }`}
          >
            {isStreaming ? <VideoOff size={14} /> : <Video size={14} />}
            {isStreaming ? 'STOP STREAM' : 'START STREAM'}
          </button>
        </div>
      </div>
    </section>
  );
}
