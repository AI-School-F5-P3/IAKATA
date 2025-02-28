import { Link, useParams } from 'react-router-dom';
import { useUserContext } from '../../context/UserContext';
import { useState } from 'react';
import "./Nav.css";
import logo from "../../assets/img/logotipo2.png";
import Logout from '../logOut/Logout';

const Nav = () => {
  const { user, userAuth, isActive } = useUserContext();
  const [openMenu, setOpenMenu] = useState(false);
  const { id } = useParams(); // Obtenemos el ID de la URL actual

  const toggleMenu = () => {
    setOpenMenu(!openMenu);
  };

  const isAdmin = user?.rol === 'admin';
  const isAuthorized = userAuth && isActive;

  // Validación de ID para desarrollo
  if (process.env.NODE_ENV === 'development' && !id) {
    console.warn("Nav: ID no detectado - Asegurar que estamos en ruta con parámetro id");
  }

  return (
    <nav className="navbar">
      <div className="logo-name">
        <img className='logo-img' src={logo} alt="logo" />
      </div>

      {isAuthorized && (
        <div className="menu-toggle" onClick={toggleMenu}>
          <div className={`bar ${openMenu ? 'active' : ''}`}></div>
          <div className={`bar ${openMenu ? 'active' : ''}`}></div>
          <div className={`bar ${openMenu ? 'active' : ''}`}></div>
        </div>
      )}

      {isAuthorized && (
        <ul className={`nav-links ${openMenu ? 'open' : ''}`}>
          {/* Elemento principal Lean Kata */}
          <li className="nav-button">
            <Link to="/home" onClick={toggleMenu}>
              Lean <span className='letter-nav'>K</span>ata
            </Link>
          </li>

          {/* Menú principal */}
          <li className="nav-button">
            <Link to="process" onClick={toggleMenu}>Crear Reto</Link>
          </li>
          <li className="nav-button">
            <Link to="home" onClick={toggleMenu}>Ver Existente</Link>
          </li>

          {/* Nuevos módulos con parámetro ID */}
          <li className="nav-button">
            <Link 
              to={`/home/reports/${id}`} 
              onClick={toggleMenu}
              state={{ challengeId: id }}
              className="nav-report-link"
            >
              📄 Informes
            </Link>
          </li>
          <li className="nav-button">
            <Link 
              to={`/home/analysis/${id}`} 
              onClick={toggleMenu}
              state={{ challengeId: id }}
              className="nav-analysis-link"
            >
              📊 Análisis
            </Link>
          </li>

          {/* Menú administrativo */}
          {isAdmin && (
            <li className="nav-button">
              <Link to="/home/user-management" onClick={toggleMenu}>
                👥 Gestión de Usuarios
              </Link>
            </li>
          )}

          {/* Perfil y logout */}
          <div className='button-profile'>
            <p className="nav-button-profile">
              👤 {user && user.name}
            </p>
            <Logout />
          </div>
        </ul>
      )}
    </nav>
  );
};

export default Nav;