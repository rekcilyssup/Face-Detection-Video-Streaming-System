import { useRef, useState, useCallback, useEffect } from 'react';
import { config } from '../config';

export function useWebcamIngest() {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const intervalRef = useRef<number | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const startCapture = useCallback(async () => {
    try {
      setError(null);
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480, facingMode: 'user' },
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }

      if (!canvasRef.current) {
        canvasRef.current = document.createElement('canvas');
        canvasRef.current.width = 640;
        canvasRef.current.height = 480;
      }

      intervalRef.current = window.setInterval(() => {
        if (!videoRef.current || !canvasRef.current) return;

        const ctx = canvasRef.current.getContext('2d');
        if (!ctx) return;

        ctx.drawImage(videoRef.current, 0, 0, 640, 480);

        canvasRef.current.toBlob(
          async (blob) => {
            if (!blob) return;
            const formData = new FormData();
            formData.append('frame', blob, 'frame.jpg');

            try {
              await fetch(config.api.ingest, { method: 'POST', body: formData });
            } catch {
              // Individual frame failures are expected under load — don't crash
            }
          },
          'image/jpeg',
          0.8,
        );
      }, config.ingest.frameIntervalMs);

      setIsStreaming(true);
    } catch (e) {
      setError(
        e instanceof Error
          ? e.message.includes('NotAllowed')
            ? 'Camera access denied. Please allow camera permissions.'
            : e.message
          : 'Failed to access webcam',
      );
    }
  }, []);

  const stopCapture = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    if (videoRef.current?.srcObject) {
      const tracks = (videoRef.current.srcObject as MediaStream).getTracks();
      tracks.forEach((t) => t.stop());
      videoRef.current.srcObject = null;
    }
    setIsStreaming(false);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => stopCapture();
  }, [stopCapture]);

  return { videoRef, isStreaming, error, startCapture, stopCapture };
}
