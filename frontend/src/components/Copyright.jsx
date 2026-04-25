import { FaInstagram, FaLinkedin, FaYoutube, FaFacebookSquare } from "react-icons/fa";
import { IoLogoGithub } from "react-icons/io";
import { useTranslation } from "react-i18next";

export default function Copyright() {
  const { t } = useTranslation();

  return (
    <div className="bg-black text-[#ccc] py-3.5 px-5 text-[0.85rem]">
      <div className="max-w-300 my-0 mx-auto flex justify-between flex-wrap gap-2.5">
        
        <div>
          {t("copyright.rights")}
        </div>

        <div className="flex items-center gap-5">
          <p>{t("copyright.followUs")}</p>

          <a
            href="https://www.instagram.com/securiva"
            target="_blank"
            rel="noopener noreferrer"
          >
            <FaInstagram
              size={25}
              className="hover:text-blue-600 hover:cursor-pointer text-white"
            />
          </a>

          <a
            href="https://www.facebook.com/securiva/"
            target="_blank"
            rel="noopener noreferrer"
          >
            <FaFacebookSquare
              size={25}
              className="hover:text-blue-600 hover:cursor-pointer text-white"
            />
          </a>

          <a
            href="https://www.linkedin.com/company/securiva/"
            target="_blank"
            rel="noopener noreferrer"
          >
            <FaLinkedin
              size={25}
              className="hover:text-blue-600 hover:cursor-pointer text-white"
            />
          </a>

          <a
            href=""
            target="_blank"
            rel="noopener noreferrer"
          >
            <FaYoutube
              size={25}
              className="hover:text-blue-600 hover:cursor-pointer text-white"
            />
          </a>

          <a
            href=""
            target="_blank"
            rel="noopener noreferrer"
          >
            <IoLogoGithub
              size={25}
              className="hover:text-blue-600 hover:cursor-pointer text-white"
            />
          </a>

        </div>
      </div>
    </div>
  );
}