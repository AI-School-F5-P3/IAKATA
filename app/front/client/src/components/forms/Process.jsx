import React, { useState, useEffect } from "react";
import { useNavigate } from 'react-router-dom';
import { postProcess, getOneProcess, updateProcess } from '../../services/processServices';
import { useForm } from 'react-hook-form';
import Swal from 'sweetalert2';
import './css/Forms.css';

const Process = ({ processId, setLoading, setEditable, isEdit = false }) => {
  const { register, formState: { errors }, handleSubmit, setValue } = useForm();
  const navigate = useNavigate();
  const [processData, setProcessData] = useState({});

  useEffect(() => {
    if (isEdit && processId) {
      const fetchData = async () => {
        const response = await getOneProcess(processId);
        const processData = response.data;
        setProcessData(processData);
        setValue("description", processData.description);
      };
      fetchData();
    }
  }, [processId, setValue, isEdit]);

  const onSubmit = async (data) => {
    try {
      if (isEdit) {
        await updateProcess(processId, data);
        Swal.fire("¡Los datos del elemento han sido actualizados correctamente!");
        setLoading(true);
        setEditable(false);
      } else {
        await postProcess(data);
        navigate('/home/tribe');
      }
    } catch (error) {
      console.error('Error:', error);
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: `Error al ${isEdit ? 'crear' : 'actualizar'} el proceso`
      });
    }
  };

  return (
    <div className={isEdit ? "form-container" : "form-box"}>
      <form className='form-create' onSubmit={handleSubmit(onSubmit)}>
        <h2>{isEdit ? "EDITAR PROCESO" : "CREAR PROCESO"}</h2>
        <div className='items'>
          <label className='label-item'>Descripción: </label>
          <textarea 
            type="text" 
            rows="10" 
            cols="50"
            {...register('description', { 
              required: 'La descripción es requerida'
            })}
          />
          {errors.description && 
            <p className="error-message">{errors.description.message}</p>
          }
        </div>
        <button className='button-forms' type="submit">
          {isEdit ? "EDITAR" : "ENVIAR"}
        </button>
        {isEdit ? (
          <>
          <button className='button-forms' onClick={() => setEditable(false)}>
            CERRAR
          </button>
          <button className='button-forms'>MEJORAR CON IA 🪄</button>
          </>
        ) : (
          <>
          <button className='button-forms' onClick={() => navigate('/home')}>
            VOLVER
          </button>
          <button className='button-forms'>MEJORAR CON IA 🪄</button>
          </>
        )}
      </form>
    </div>
  );
};

export default Process;