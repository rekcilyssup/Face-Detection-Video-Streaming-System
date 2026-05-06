import { ScanFace, Filter, AlertCircle } from 'lucide-react';
import type { RoiDetection, ConnectionState } from '../types';

interface DetectionPanelProps {
  latestRoi: RoiDetection | null;
  roiHistory: RoiDetection[];
  connectionState: ConnectionState;
}

const ROI_FIELDS: { key: keyof RoiDetection; label: string }[] = [
  { key: 'x', label: 'X' },
  { key: 'y', label: 'Y' },
  { key: 'width', label: 'W' },
  { key: 'height', label: 'H' },
];

function getConfidenceColor(confidence: number): string {
  const pct = confidence * 100;
  if (pct > 95) return 'text-secondary';
  if (pct > 80) return 'text-tertiary';
  return 'text-outline-variant';
}

export default function DetectionPanel({
  latestRoi,
  roiHistory,
  connectionState,
}: DetectionPanelProps) {
  const isConnected = connectionState === 'connected';
  const hasFace = latestRoi !== null && latestRoi.confidence > 0;

  return (
    <section id="detection-panel" className="w-full lg:w-[35%] flex flex-col gap-xs h-full">
      {/* Status Bar */}
      <div className="card-surface border-thin p-md flex justify-between items-center">
        <div className="flex items-center gap-sm">
          {hasFace ? (
            <>
              <ScanFace className="text-secondary" size={24} fill="currentColor" fillOpacity={0.2} />
              <span className="font-h2 text-h2 text-secondary">Face Detected</span>
            </>
          ) : (
            <>
              <AlertCircle className="text-outline-variant" size={24} />
              <span className="font-h2 text-h2 text-outline-variant">
                {isConnected ? 'No Face Detected' : 'Waiting for Stream'}
              </span>
            </>
          )}
        </div>
        <span className="font-data-mono text-data-mono text-outline-variant">
          {latestRoi?.detected_at
            ? new Date(latestRoi.detected_at).toLocaleTimeString()
            : '--:--:--.---'}
        </span>
      </div>

      {/* ROI Metrics */}
      <div className="card-surface border-thin p-md flex flex-col gap-md">
        <h3 className="font-label-caps text-label-caps text-outline-variant uppercase tracking-wider">
          Region of Interest
        </h3>
        <div className="grid grid-cols-2 gap-gutter bg-outline-variant/30 border-thin">
          {ROI_FIELDS.map(({ key, label }) => (
            <div key={key} className="sub-surface p-sm flex justify-between items-center">
              <span className="font-body-sm text-outline-variant">{label}</span>
              <span className="font-data-mono text-primary">
                {latestRoi && hasFace ? String(latestRoi[key]) : '--'}
              </span>
            </div>
          ))}
        </div>

        <div className="flex flex-col gap-xs mt-xs">
          <div className="flex justify-between items-center">
            <span className="font-body-sm text-outline-variant">Confidence</span>
            <span className="font-data-mono text-secondary">
              {latestRoi && hasFace
                ? `${(latestRoi.confidence * 100).toFixed(1)}%`
                : '--.-%'}
            </span>
          </div>
          <div className="h-1 w-full bg-surface-container-highest border-thin">
            <div
              className="h-full bg-secondary transition-all duration-300"
              style={{ width: latestRoi && hasFace ? `${latestRoi.confidence * 100}%` : '0%' }}
            />
          </div>
        </div>
      </div>

      {/* Detection Log */}
      <div className="card-surface border-thin flex-1 flex flex-col min-h-[300px] overflow-hidden">
        <div className="p-sm border-b-thin bg-surface-container-highest flex justify-between items-center">
          <h3 className="font-label-caps text-label-caps text-outline-variant uppercase tracking-wider">
            Detection Log
          </h3>
          <Filter className="text-outline-variant" size={16} />
        </div>
        <div className="flex-1 overflow-y-auto">
          <table className="w-full text-left border-collapse">
            <thead className="sticky top-0 bg-surface-container-highest z-10 border-b-thin">
              <tr>
                <th className="p-sm font-label-caps text-label-caps text-outline-variant font-normal">Frame</th>
                <th className="p-sm font-label-caps text-label-caps text-outline-variant font-normal">BBox [x,y,w,h]</th>
                <th className="p-sm font-label-caps text-label-caps text-outline-variant font-normal">Conf</th>
                <th className="p-sm font-label-caps text-label-caps text-outline-variant font-normal text-right">Time</th>
              </tr>
            </thead>
            <tbody className="font-data-mono text-[11px] text-on-surface-variant">
              {roiHistory.length === 0 ? (
                <tr>
                  <td colSpan={4} className="p-md text-center text-outline-variant font-body-sm italic">
                    {isConnected ? 'Waiting for detections…' : 'Start stream to see detections'}
                  </td>
                </tr>
              ) : (
                roiHistory.map((roi, i) => {
                  const detected = roi.confidence > 0;
                  const confPct = (roi.confidence * 100).toFixed(1);
                  return (
                    <tr
                      key={roi.id ?? i}
                      className={`border-b-thin hover:bg-[#252936] transition-colors ${
                        i === 0 ? 'bg-surface-container-low/50' : ''
                      }`}
                    >
                      <td className={`p-sm ${!detected ? 'text-outline-variant' : ''}`}>
                        #{roi.frame_number}
                      </td>
                      <td className={`p-sm ${!detected ? 'text-outline-variant italic' : 'text-primary'}`}>
                        {detected
                          ? `[${roi.x}, ${roi.y}, ${roi.width}, ${roi.height}]`
                          : 'No face detected'}
                      </td>
                      <td className={`p-sm ${!detected ? 'text-outline-variant italic' : getConfidenceColor(roi.confidence)}`}>
                        {detected ? `${confPct}%` : '--'}
                      </td>
                      <td className="p-sm text-outline-variant text-right">
                        {new Date(roi.detected_at).toLocaleTimeString()}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
