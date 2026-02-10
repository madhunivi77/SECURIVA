function Card({ image, title, text }) {
  return (
    <div className="card bg-white w-96 shadow-sm">
      <figure>
        <img
          src={image}
          alt={title} />
      </figure>
      <div className="card-body items-center text-center">
        <h2 className="card-title text-2xl">{title}</h2>
        <p className="text-lg">{text}</p>
      </div>
    </div>
  );
}

export default Card;