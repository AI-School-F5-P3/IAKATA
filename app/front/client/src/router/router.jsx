import { createBrowserRouter } from "react-router-dom";
import LayoutPublic from "../components/layout/LayoutPublic";
import LayoutPrivate from "../components/layout/LayoutPrivate";
import Landing from '../pages/Landing/Landing.jsx';
import Register from '../pages/Register.jsx';
import Home from "../pages/home/Home";
import Challenge from '../components/forms/Challenge';
import ActualState from "../components/forms/ActualState";
import Process from '../components/forms/Process';
import Tribe from '../components/forms/Tribe';
import NotFound from "../pages/notfound/NotFound";
import Card from "../components/card/Card";
import AboutUs from "../pages/AbouUs/AboutUs"
import RegisterForm from "../components/forms/RegisterForm.jsx";
import Login from "../pages/login/Login.jsx";
import UserManagement from "../pages/userManagement/UserManagement";

const router = createBrowserRouter([
  {
    path: '/',
    element: <LayoutPublic />,
    children: [
      {
        index: true,
        element: <Landing />
      },
      {
        path: "register",
        element: <Register />,
      },
      {
        path: "registerform", 
        element: <RegisterForm/>,
      },
      {
        path: "login",
        element: <Login />,
      }
    ]
  },
  {
    path: '/home',
    element: <LayoutPrivate />,
    errorElement: <NotFound />,
    children: [
      {
        index: true,
        element: <AboutUs/>,
      },
      {
        path: "home",
        element: <Home/>
      },
      {
        path: "card/:id",
        element: <Card/>
      },
      {
        path: "process",
        element: <Process/>
      },
      {
        path: "tribe",
        element: <Tribe/>
      },
      {
        path: "challenge",
        element: <Challenge/>,
      },
      {
        path: "actualstate",
        element: <ActualState/>,
      },
      {
        path: "user-management",
        element: <UserManagement/>,
      },
      {
        path: "*",
        element: <NotFound/>
      }
    ],
  }
]);

export default router;

