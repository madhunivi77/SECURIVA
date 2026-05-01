import { Link } from "react-router-dom";

function NavOption({label, target, theme, onClick}){
    return (
        <Link to={target}>
            <button className='bg-none rounded-md px-1.5 cursor-pointer' style={{color: theme}} onClick={onClick}>
                {label}
            </button>
        </Link>
    );
}

export default NavOption;