function CenteredArrow({ width = 50, height = 100, color = "white" }) {
  return (
    <div class="flex justify-center mx-5 my-0">
      <svg
        width={width}
        height={height}
        viewBox="0 0 24 24"
        fill="none"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        {/* Vertical line */}
        <line x1="12" y1="0" x2="12" y2="18" />
        {/* Arrowhead */}
        <polyline points="6,12 12,18 18,12" />
      </svg>
    </div>
  );
}

export default CenteredArrow;