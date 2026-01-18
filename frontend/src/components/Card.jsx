function Card({ image, title, text }) {
  return (
    <div
      className="bg-[#f7f7f7] p-5 border-r-16 border-solid border rounded-2xl shadow-md border-[#e5e5e5] text-center"
    >
      <img
        src={image}
        alt={title}
        className="w-full h-auto"
      />

      <h3 className="w-full mb-2.5 text-[25px]">
        {title}
      </h3>

      <p className="w-full text-[15px]/6"> 
        {text}
      </p>
    </div>
  );
}

export default Card;