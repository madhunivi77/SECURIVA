import { Link } from "react-router-dom";

function NavOption({label, target, theme}){
    return (
        <Link to={target}>
            <button className='bg-none rounded-md px-1.5 py-3 cursor-pointer' style={{color: theme}}>
                {label}
            </button>
        </Link>
    );
}

export default NavOption;