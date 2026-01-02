import React from "react";
import { useState, useEffect } from "react";

function NavOption({label, target, setPage}){
    return (
        <button
              onClick={() => setPage(target)}
              style={{
                background: "none",
                //border: `1px solid ${theme.border}`,
                color: "#0d2b66",
                borderRadius: "6px",
                padding: "6px 12px",
                cursor: "pointer",
              }}
            >
              {label}
        </button>
    );
}

export default NavOption;