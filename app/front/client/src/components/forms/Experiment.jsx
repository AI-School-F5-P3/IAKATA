import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { postExperiment, uploadImage, getOneExperiment, updateExperiment} from '../../services/experimentServices';
import './css/Forms.css';
import Swal from 'sweetalert2';

const Experiment = ({ 
    editExperimentId, 
    editHypothesisId, 
    setLoading, 
    setEditExperiment, 
    isEdit = false 
}) => {
    const { register, handleSubmit, formState: { errors }, setValue, watch } = useForm();
    const [imageUrl, setImageUrl] = useState('');
    const [experimentData, setExperimentData] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            if (isEdit && editExperimentId) {
                try {
                    const response = await getOneExperiment(editExperimentId);
                    const data = response.data;
                    setExperimentData(data);
                    setImageUrl(data.image);
                    
                    Object.keys(data).forEach(key => {
                        setValue(key, data[key]);
                    });
                } catch (error) {
                    console.error('Error fetching experiment:', error);
                }
            }
        };
        fetchData();
    }, [isEdit, editExperimentId, setValue]);

    const handleImageUpload = async (file) => {
        const imageData = new FormData();
        imageData.append("file", file);
        imageData.append("upload_preset", "LeanKata");
        const response = await uploadImage(imageData);
        return response.secure_url;
    };

    const onSubmit = async (data) => {
        try {
            let finalImageUrl = imageUrl;
            
            if (data.image && data.image[0]) {
                finalImageUrl = await handleImageUpload(data.image[0]);
            }

            const formData = {
                ...data,
                image: finalImageUrl,
                hyphotesis_id: editHypothesisId
            };

            if (isEdit) {
                await updateExperiment(editExperimentId, formData);
                Swal.fire('¡Experimento actualizado correctamente!');
            } else {
                await postExperiment(formData);
                Swal.fire('¡Experimento creado correctamente!');
            }

            setLoading(true);
            setEditExperiment(false);
        } catch (error) {
          console.error('Error:', error);
        }
    };

  const validateDateRange = (startDate, endDate) => {
    if (!startDate || !endDate) return true;
    return new Date(startDate) < new Date(endDate) || "La fecha de inicio debe ser anterior a la fecha de fin";
  };
  
  const validateHypothesisDate = (startDate, hypothesisDate) => {
    if (!startDate || !hypothesisDate) return true;
    return new Date(hypothesisDate) < new Date(startDate) || "La fecha de planteamiento del experimento debe ser anterior a la fecha de inicio";
  };

  const closeForm = () => {
    setEditExperiment(false);
  };

  return (
    <div className="form-container">
    <form className='form-create' onSubmit={handleSubmit(onSubmit)}>
    <h2> CREAR EXPERIMENTO </h2>
      <div className='items'>
        <label className='label-item'>Descripción</label>
        <textarea type="text" rows="10" cols="50"{...register('description', { required: true })} />
        {errors.description && <p className="error-message">La descripción es requerida</p>}
      </div>
      <div className='items'>
        <label className='label-item'>Fecha de inicio:</label>
        <div className='date-input-wrapper'>
        <input type="date" {...register('start_date', { required: true, validate: value => validateHypothesisDate(value, watch('hypothesis_date')) })} />
        <span className='date-icon'>&#x1F4C5;</span>
        </div>
        {errors.start_date && <p className="error-message">{errors.start_date.message}</p>}
      </div>
      <div className='items'>
        <label className='label-item'>Fecha de fin:</label>
        <div className='date-input-wrapper'>
        <input type="date" {...register('end_date', { required: true, validate: value => validateDateRange(watch('start_date'), value) })} />
        <span className='date-icon'>&#x1F4C5;</span>
        </div>
        {errors.end_date && <p className="error-message">{errors.end_date.message}</p>}
      </div>
      <div className='items'>
        <label className='label-item'>Objetivos:</label>
        <input type="text" {...register('goals', { required: true })} />
        {errors.goals && <p className="error-message">Los objetivos son requeridos</p>}
      </div>
      <div className='items'>
        <label className='label-item'>Metodología:</label>
        <input type="text" {...register('methodology', { required: true })} />
        {errors.methodology && <p className="error-message">La metodología es requerida</p>}
      </div>
      <div className='items'>
        <label className='label-item'>Variables:</label>
        <input type="text" {...register('variables', { required: true })} />
        {errors.variables && <p className="error-message">Las variables son requeridas</p>}
      </div>
      <div className='items'>
        <label className='label-item'>Grupo de control:</label>
        <input type="text" {...register('control_group', { required: true })} />
        {errors.control_group && <p className="error-message">El grupo de control es requerido</p>}
      </div>
      <div className='items'>
        <label className='label-item'>Criterios de éxito:</label>
        <input type="text" {...register('success_criteria', { required: true })} />
        {errors.success_criteria && <p className="error-message">Los criterios de éxito son requeridos</p>}
      </div>
      <div className='items'>
        <label className='label-item'>Responsable:</label>
        <input type="text" {...register('responsible', { required: true })} />
        {errors.responsible && <p className="error-message">El responsable es requerido</p>}
      </div>
      <div className='items'>
        <label className='label-item'>Estado del experimento:</label>
        <input type="text" {...register('state_experiment', { required: true })} />
        {errors.state_experiment && <p className="error-message">El estado del experimento es requerido</p>}
      </div>
      <div className='items'>
        <label className='label-item'>Imagen:</label>
        <input className='button-image' type="file" {...register('image')} />
        {errors.image && <p className="error-message">Por favor, adjunta una imagen</p>}
      </div>
      <button type="submit" className='button-forms'>Enviar</button>
     <button className='button-forms' onClick={closeForm}>Cerrar</button>
     <button className='button-forms'>MEJORAR CON IA 🪄</button>
    </form>
    </div>
  )
}

export default Experiment;