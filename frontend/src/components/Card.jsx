function Card({ image, title, text }) {
  return (
    <div className="card bg-white w-120 shadow-sm border-3 border-white">
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