function Card({ image, title, text }) {
  return (
    <div className="card bg-white w-96 shadow-sm">
      <figure>
        <img
          src={image}
          alt={title} />
      </figure>
      <div className="card-body">
        <h2 className="card-title">{title}</h2>
        <p>{text}</p>
      </div>
    </div>
  );
}

export default Card;