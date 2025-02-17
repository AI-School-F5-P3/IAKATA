import React, { useEffect } from "react";
import { Outlet, Navigate } from "react-router-dom";
import { useUserContext } from "../../context/UserContext";
import Nav from "../nav/Nav";
import Footer from "../footer/footer";
import Chatbot from "../chatbot/Chatbot";

const LayoutPrivate = () => {  
    const { userAuth, isActive } = useUserContext();
    
    useEffect(() => {
        console.log('Auth State:', { userAuth, isActive });
    }, [userAuth, isActive]);

    if (!userAuth || !isActive) {
        console.log('Redirecting to login');
        return <Navigate to="/login" replace />;
    }

    return (
        <>
            <Nav />
            <main>
                <Outlet />
            </main>
            <Chatbot/>
            <Footer />
        </>
    );
};

export default LayoutPrivate;