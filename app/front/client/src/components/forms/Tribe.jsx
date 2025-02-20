import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { postTribe, getOneTribe, updateTribe } from '../../services/tribeServices';
import Swal from 'sweetalert2';
import './css/Forms.css';

const Tribe = ({ tribeId, setEditable, isEdit = false }) => {
  const { register, formState: { errors }, handleSubmit, setValue } = useForm();
  const navigate = useNavigate();
  const [tribeData, setTribeData] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isEdit && tribeId) {
      const fetchData = async () => {
        const response = await getOneTribe(tribeId);
        const tribeData = response.data;
        setTribeData(tribeData);
        setValue('name_tribe', tribeData.name_tribe);
        setValue('team_members', tribeData.team_members);
        setValue('password', tribeData.password);
        console.log(tribeData);
      };
      fetchData();
    }
  }, [tribeId, setValue, isEdit]);

   const onSubmit = async (data) => {
    try {
      if (isEdit) {
        await updateTribe(tribeId, data);
        Swal.fire('¡Los datos han sido actualizados correctamente!');
        setLoading(true);
        setEditable(false);
      } else {
        await postTribe(data);
        navigate('/home/challenge');
      }
    } catch (error) {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: `Error al ${isEdit ? 'actualizar' : 'crear'} la tribu`
      });
    }
  };

  const handleClose = () => isEdit ? setEditable(false) : navigate('/home');

  return (
    <div className={isEdit ? "form-container" : "form-box"}>
      <form className='form-create' onSubmit={handleSubmit(onSubmit)}>
        <h2>{isEdit ? "EDITAR TRIBU" : "CREAR TRIBU"}</h2>
        <div className='items'>
          <label className='label-item'>Nombre de la Tribu</label>
          <input
            type="text"
            {...register('name_tribe', { required: true })}
          />
          {errors.name_tribe && <p className="error-message">El nombre es requerido</p>}
        </div>
        <div className='items'>
          <label className='label-item'>Miembros de la tribu</label>
          <textarea
            rows="10"
            cols="50"
            {...register('team_members', { required: true })}
          />
          <div className="form-group">
            <label>Contraseña para el grupo del reto</label>
            <input
              type="password"
              className="form-control"
              {...register("password")}
              placeholder="Ingrese una contraseña para proteger el reto"
            />
          </div>
          {errors.team_members && <p className="error-message">Los miembros son requeridos</p>}
        </div>
        <button className='button-forms' type="submit">
          {isEdit ? "GUARDAR" : "CREAR"}
        </button>
        <button
          type="button"
          className='button-forms'
          onClick={handleClose}
        >
          {isEdit ? "CANCELAR" : "VOLVER"}
        </button>
      </form>
    </div>
  );
};

export default Tribe;