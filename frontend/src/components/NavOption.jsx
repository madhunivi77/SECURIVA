function NavOption({label, target, setPage}){
    return (
        <button
              onClick={() => setPage(target)}
              className="bg-none text-[#0d2b66] rounded-md px-1.5 py-3 cursor-pointer"
            >
              {label}
        </button>
    );
}

export default NavOption;