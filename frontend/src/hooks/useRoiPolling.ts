import { useState, useEffect, useRef } from 'react';
import { config } from '../config';
import type { RoiDetection } from '../types';

export function useRoiPolling(enabled: boolean) {
  const [latestRoi, setLatestRoi] = useState<RoiDetection | null>(null);
  const [roiHistory, setRoiHistory] = useState<RoiDetection[]>([]);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<number | null>(null);

  useEffect(() => {
    if (!enabled) {
      if (intervalRef.current) clearInterval(intervalRef.current);
      return;
    }

    const fetchRoi = async () => {
      try {
        const res = await fetch(config.api.roi);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json = await res.json();

        // Handle both envelope { data: { detections: [...] } } and flat array
        const detections: RoiDetection[] =
          json.data?.detections ?? json.detections ?? (Array.isArray(json) ? json : []);

        if (detections.length > 0) {
          setLatestRoi(detections[0]);
          setRoiHistory(detections.slice(0, 50));
        }
        setError(null);
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Failed to fetch ROI');
      }
    };

    fetchRoi();
    intervalRef.current = window.setInterval(fetchRoi, config.polling.roiIntervalMs);

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [enabled]);

  return { latestRoi, roiHistory, error };
}
