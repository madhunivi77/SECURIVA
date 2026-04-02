import { FaInstagram, FaLinkedin, FaYoutube, FaFacebookSquare } from "react-icons/fa";
import { IoLogoGithub } from "react-icons/io";

export default function Copyright() {
  return (
    <div className="bg-black text-[#ccc] py-3.5 px-5 text-[0.85rem]">
      <div className="max-w-300 my-0 mx-auto flex justify-between flex-wrap gap-2.5">
        <div>
          © 2026 SecuriVA. All rights reserved.  Powered by Kimuntu Power Inc.
        </div>

        <div className="flex items-center gap-5">
          <p>Follow Us</p>
          <a href="https://www.instagram.com/securiva" target="_blank"><FaInstagram size={25} className="hover:text-blue-600 hover:cursor-pointer text-white"/></a>
          <a href="https://www.facebook.com/securiva/" target="_blank"><FaFacebookSquare size={25} className="hover:text-blue-600 hover:cursor-pointer text-white"/></a>
          <a href="https://www.linkedin.com/company/securiva/" target="_blank"><FaLinkedin size={25} className="hover:text-blue-600 hover:cursor-pointer text-white"/></a>
          <a href="" target="_blank"><FaYoutube size={25} className="hover:text-blue-600 hover:cursor-pointer text-white"/></a>
          <a href="" target="_blank"><IoLogoGithub size={25} className="hover:text-blue-600 hover:cursor-pointer text-white"/></a>
        </div>
      </div>
    </div>
  );
}