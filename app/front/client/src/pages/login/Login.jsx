import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useUserContext } from '../../context/UserContext';
import { loginUser } from '../../services/logReg';
import '../../components/forms/css/RegForm.css';
import Swal from 'sweetalert2';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [emailError, setEmailError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { updateSessionState } = useUserContext();

  const showClosingSessionAlert = () => {
    return Swal.fire({
      title: 'Cerrando sesión anterior...',
      html: `
        <div class="loading-message">
          <p>Estamos cerrando la sesión activa</p>
          <p class="small-text">Esto puede tomar unos segundos</p>
        </div>
      `,
      allowOutsideClick: false,
      showConfirmButton: false,
      didOpen: () => {
        Swal.showLoading();
      },
      customClass: {
        popup: 'swal-custom-popup',
        title: 'swal-custom-title',
        content: 'swal-custom-content',
        loader: 'custom-loader'
      }
    });
  };

  const showWelcomeAlert = async (userData) => {
    let timerInterval;
    await Swal.fire({
      title: `¡Bienvenido ${userData.name}!`,
      html: 'Estamos preparando todo para ti...',
      timer: 3000,
      timerProgressBar: true,
      showConfirmButton: false,
      allowOutsideClick: false,
      customClass: {
        popup: 'swal-custom-popup',
        title: 'swal-custom-title',
        content: 'swal-custom-content',
        timerProgressBar: 'timer-progress-bar-custom'
      },
      didOpen: () => {
        const timer = Swal.getPopup().querySelector('b');
        if (timer) {
          timerInterval = setInterval(() => {
            timer.textContent = Math.ceil(Swal.getTimerLeft() / 1000);
          }, 100);
        }
      },
      willClose: () => {
        clearInterval(timerInterval);
      }
    });
  };

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    setIsLoading(true);
    setEmailError('');
    setPasswordError('');

    try {
      const data = await loginUser(email, password);
      if (data.success) {
        await showWelcomeAlert(data.data);
        updateSessionState(data.data);
        navigate('/home');
      }
    } catch (error) {
      console.error('Login error:', error);

      if (error.message === 'Active session exists' || error.response?.data?.data?.isActive) {
        const result = await Swal.fire({
          title: 'Sesión Activa',
          text: 'Ya existe una sesión iniciada para este usuario. ¿Deseas cerrarla?',
          icon: 'warning',
          showCancelButton: true,
          confirmButtonColor: '#002661',
          cancelButtonColor: '#ECF0F1',
          confirmButtonText: 'Sí, cerrar sesión',
          cancelButtonText: 'Mantener sesión actual',
          allowOutsideClick: false,
          customClass: {
            popup: 'swal-custom-popup',
            title: 'swal-custom-title',
            content: 'swal-custom-content',
            confirmButton: 'swal-custom-confirm',
            cancelButton: 'swal-custom-cancel'
          }
        });

        if (result.isConfirmed) {
          showClosingSessionAlert();
          try {
            console.log('Forcing login...');
            const retryData = await loginUser(email, password, true);
            
            if (retryData.success) {
              Swal.close();
              await showWelcomeAlert(retryData.data);
              updateSessionState(retryData.data);
              navigate('/home');
            }
          } catch (retryError) {
            console.error('Force login error:', retryError);
            Swal.close();
            setPasswordError('Error al forzar el cierre de sesión. Intente nuevamente.');
          }
        }
      } else if (error.response?.status === 401) {
        setPasswordError('Email o contraseña incorrectos');
      } else {
        setPasswordError(error.message || 'Error al iniciar sesión');
      }
    } finally {
      setIsLoading(false);
      if (Swal.isVisible()) {
        Swal.close();
      }
    }
  };

  return (
    <div className="form-container">
      <form onSubmit={handleSubmit} className="form-create-log">
        <h2>Iniciar Sesión</h2>
        <div className="items">
          <label className="label-item" htmlFor="email">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => {
              setEmail(e.target.value);
              setEmailError('');
            }}
            required
            className="input-reg"
            id="email"
            placeholder="hola@gmail.com"
            disabled={isLoading}
          />
          {emailError && <p className="text-[#FB005A] text-xs">{emailError}</p>}
        </div>

        <div className="items">
          <label className="label-item" htmlFor="password">Contraseña</label>
          <div className="relative">
            <input
              type={showPassword ? "text" : "password"}
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                setPasswordError('');
              }}
              required
              className="input-reg"
              id="password"
              placeholder="Ingresa tu contraseña"
              disabled={isLoading}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-transparent border-none cursor-pointer text-[#FB005A]"
            >
              {showPassword ? '🔒' : '👁️'}
            </button>
          </div>
          {passwordError && <p className="text-[#FB005A] text-xs">{passwordError}</p>}
        </div>

        <div className="items">
          <button 
            className="button-forms-log" 
            type="submit"
            disabled={isLoading}
          >
            {isLoading ? 'Iniciando sesión...' : 'Iniciar sesión'}
          </button>
          <p className="paragraph-reg">
            ¿No tienes cuenta? <Link to="/register" className="button-reg">Regístrate</Link>
          </p>
        </div>
      </form>
    </div>
  );
};

export default Login;