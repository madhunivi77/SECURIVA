import { Link } from "react-router-dom";

function NavOption({label, target}){
    return (
        <Link to={target}>
            <button className="bg-none text-[#0d2b66] rounded-md px-1.5 py-3 cursor-pointer">
                {label}
            </button>
        </Link>
    );
}

export default NavOption;