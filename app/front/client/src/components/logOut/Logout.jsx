import { useUserContext } from '../../context/UserContext'; 
import "../nav/Nav.css";
import './Logout.css';
import profile from '../../assets/img/profile.png';

const LogOut = () => {
    const { logout, setIsActive } = useUserContext();

    const handleLogout = async () => {
        try {
            setIsActive(false);
            await logout();
        } catch (error) {
            console.error('Error during logout:', error);
        }
    };

    return (
        <button className="Btn" onClick={handleLogout}>
            <img className="icon-profile" src={profile} alt="Profile"/>
            <div className="sign"></div>
            <div className="text">Cerrar sesión</div>
        </button>
    );
};

export default LogOut;