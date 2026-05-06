export default function Footer() {
  return (
    <footer className="flex justify-between items-center px-lg py-xs w-full border-t border-outline-variant/20 bg-surface-container-lowest">
      <span className="font-h1 text-h1 text-primary">FaceStream</span>
      <span className="font-body-sm text-body-sm text-outline-variant">
        © {new Date().getFullYear()} FaceStream. v1.0.0
      </span>
      <div className="flex gap-md font-body-sm text-body-sm">
        <a className="text-on-surface-variant hover:text-on-surface transition-colors" href="#">
          Documentation
        </a>
      </div>
    </footer>
  );
}
