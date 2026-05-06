import Header from './components/Header';
import VideoFeed from './components/VideoFeed';
import DetectionPanel from './components/DetectionPanel';
import Footer from './components/Footer';
import { useStreamConnection } from './hooks/useStreamConnection';
import { useWebcamIngest } from './hooks/useWebcamIngest';
import { useRoiPolling } from './hooks/useRoiPolling';

export default function App() {
  const stream = useStreamConnection();
  const ingest = useWebcamIngest();
  const { latestRoi, roiHistory } = useRoiPolling(
    stream.connectionState === 'connected',
  );

  const handleToggleStream = async () => {
    if (ingest.isStreaming) {
      ingest.stopCapture();
      stream.disconnect();
    } else {
      stream.connect();
      await ingest.startCapture();
    }
  };

  return (
    <div className="min-h-screen flex flex-col font-body-base bg-[#0f1117] text-[#d3e4fe]">
      <Header connectionState={stream.connectionState} />
      <main className="flex-1 p-xs flex flex-col lg:flex-row gap-xs overflow-hidden">
        <VideoFeed
          currentFrame={stream.currentFrame}
          fps={stream.fps}
          isStreaming={ingest.isStreaming}
          connectionState={stream.connectionState}
          webcamRef={ingest.videoRef}
          onToggleStream={handleToggleStream}
          error={ingest.error}
        />
        <DetectionPanel
          latestRoi={latestRoi}
          roiHistory={roiHistory}
          connectionState={stream.connectionState}
        />
      </main>
      <Footer />
    </div>
  );
}
