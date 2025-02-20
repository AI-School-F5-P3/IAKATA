import React from 'react';
import ReactDOM from 'react-dom/client';
import { RouterProvider } from 'react-router-dom';
import router from './router/router.jsx';
import { SocketProvider } from './context/SocketContext';
import UserProvider from "./context/UserContext";

ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
            <SocketProvider>
                <UserProvider>
                    <RouterProvider router={router} />
                </UserProvider>
            </SocketProvider>
    </React.StrictMode>
);