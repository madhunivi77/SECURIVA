

function Sponsors({ className}) {
  // Combine internal classes with the passed className prop
  const combinedClasses = `${className || ''}`.trim();
  return (
    <div className={combinedClasses}>
        <h2>Our partners play a key role in advancing the SecuriVA ecosystem.</h2>
        <div className="flex overflow-hidden py-6 justify-between">
            <img src={"/LOGOS(46).png"} className="h-auto w-50" />
            <img src={"/LOGOS(47).png"} className="w-50" />
            <img src={"/LOGOS(48).png"} className="w-50" />
            <img src={"/LOGOS(49).png"} className="w-50" />
        </div>
    </div>
);
}

export default Sponsors;