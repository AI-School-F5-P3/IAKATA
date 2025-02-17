import RegisterForm from '../components/forms/RegisterForm';
import { Link } from 'react-router-dom';

const Register = () => { 
  return (
    <div className="flex items-center justify-center min-h-screen bg-neutral-900">
      <div className="text-center">
        <Link to="/" />
        <RegisterForm />
      </div>
    </div>
  );
}

export default Register;