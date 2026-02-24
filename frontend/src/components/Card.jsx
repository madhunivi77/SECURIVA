function Card({ className, image, title, text }) {
  // Combine internal classes with the passed className prop
  const combinedClasses = `card bg-white shadow-sm border-3 border-white ${className || ''}`.trim();
  return (
    <div className={combinedClasses}>
      <figure>
        <img
          src={image}
          alt={title} />
      </figure>
      <div className="card-body items-center text-center">
        <h2 className="card-title text-3xl">{title}</h2>
        <p className="text-xl">{text}</p>
      </div>
    </div>
  );
}

export default Card;