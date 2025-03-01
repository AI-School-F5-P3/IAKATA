import { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { useForm } from "react-hook-form";
import {
  postActualState,
  getOneActualState,
  updateActualState,
} from "../../services/actualStateServices";
import { useWebSocket } from "../../context/SocketContext";
import Swal from "sweetalert2";
import "./css/Forms.css";

// Importar el componente ImproveWithAIButton
import ImproveWithAIButton from '../buttonIa/ImproveWithAIButton';

const ActualState = ({
  actualStateId,
  challengeId,
  setEditable,
  isEdit = false,
  setLoading, // Asegúrate de que esta prop se pase correctamente
}) => {
  const {
    handleSubmit,
    register,
    formState: { errors },
    setValue,
    getValues, // Añadir getValues para pasar a ImproveWithAIButton
    trigger, // Añadir trigger para validar después de cambiar valores
  } = useForm();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isImproving, setIsImproving] = useState(false); // Estado para el botón de IA
  const { WS_EVENTS, sendMessage } = useWebSocket();
  const [createActual, setCreateActual] = useState(true);
  const [currentDate] = useState(new Date().toISOString().split("T")[0]);
  
  // Definir el identificador del formulario para la IA
  const idForm = "AC"; // Identificador para estado actual
  
  useEffect(() => {
    if (isEdit && actualStateId) {
      const fetchData = async () => {
        try {
          const response = await getOneActualState(actualStateId);
          if (response?.data) {
            Object.entries(response.data).forEach(([key, value]) => {
              setValue(key, value);
            });
          }
        } catch (error) {
          console.error("Error fetching:", error);
          Swal.fire({
            icon: "error",
            title: "Error",
            text: "Error al cargar el estado actual",
            confirmButtonColor: "#002661",
            background: '#ECF0F1',
            customClass: {
                popup: "swal-custom-popup",
                title: "swal-custom-title",
                content: "swal-custom-content",
                confirmButton: "swal-custom-confirm"
            }
          });
        }
      };
      fetchData();
    } else {
      setValue("date", currentDate);
    }
  }, [actualStateId, currentDate, setValue, isEdit]);

  // Versión mejorada para manejar diferentes formatos de respuesta
const onSubmit = async (data) => {
  console.log("Iniciando onSubmit con data:", data);
  console.log("challengeId:", challengeId);
  console.log("actualStateId:", actualStateId);
  console.log("isEdit:", isEdit);
  
  if (!data.description?.trim()) {
      console.error("Error: Description is empty");
      Swal.fire({
          icon: "error",
          title: "Error",
          text: "La descripción no puede estar vacía",
          customClass: {
              popup: "swal-custom-popup",
              title: "swal-custom-title",
              confirmButton: "swal-custom-confirm",
          }
      });
      return;
  }
  
  if (!challengeId) {
      console.error("Error: No challengeId provided");
      Swal.fire({
          icon: "error",
          title: "Error",
          text: "No se ha proporcionado el ID del reto",
          customClass: {
              popup: "swal-custom-popup",
              title: "swal-custom-title",
              confirmButton: "swal-custom-confirm",
          }
      });
      return;
  }

  try {
      setIsSubmitting(true);
      
      const formData = {
          description: data.description.trim(),
          date: data.date,
          challenge_id: challengeId
      };
      
      console.log("Enviando formData:", formData);
      console.log("Modo:", isEdit ? "actualizar" : "crear");
      
      let response;
      
      if (isEdit) {
          console.log("Actualizando estado actual con ID:", actualStateId);
          response = await updateActualState(actualStateId, formData);
      } else {
          console.log("Creando nuevo estado actual");
          response = await postActualState(formData);
      }
      
      console.log("Respuesta completa:", response);
      
      // Extraer los datos relevantes de la respuesta, manejando diferentes formatos
      let responseData;
      
      if (response?.data) {
          responseData = response.data;
      } else if (response && typeof response === 'object') {
          // Si response es un objeto pero no tiene data, usamos el response directamente
          responseData = response;
      }
      
      console.log("Datos extraídos de la respuesta:", responseData);

      if (responseData) {
          console.log("Preparando payload para WebSocket");
          
          const wsPayload = {
              ...responseData,
              challenge_id: challengeId,
              type: isEdit ? "update" : "create",
              timestamp: Date.now(),
          };
          
          console.log("Enviando mensaje WebSocket:", wsPayload);
          sendMessage(WS_EVENTS.ACTUAL_STATE, wsPayload);
          
          // Manejar setLoading de forma segura
          if (typeof setLoading === 'function') {
              console.log("Ejecutando setLoading(true)");
              setLoading(true);
          } else {
              console.warn("setLoading no es una función o no está definida");
          }
          
          console.log("Ejecutando setEditable(false)");
          setEditable(false);

          Swal.fire({
              icon: 'success',
              title: '¡Éxito!',
              text: `Estado actual ${isEdit ? 'actualizado' : 'creado'} correctamente`,
              customClass: {
                  popup: "swal-custom-popup",
                  title: "swal-custom-title",
                  confirmButton: "swal-custom-confirm",
              }
          });
      } else {
          throw new Error("No se pudieron extraer datos de la respuesta");
      }
  } catch (error) {
      console.error("Error en onSubmit:", error);
      console.error("Detalles del error:", error.response || error.message || error);
      
      Swal.fire({
          icon: "error",
          title: "Error",
          text: `No se pudo ${isEdit ? "actualizar" : "crear"} el estado actual. ${error.message || ''}`,
          customClass: {
              popup: "swal-custom-popup",
              title: "swal-custom-title",
              confirmButton: "swal-custom-confirm",
          }
      });
  } finally {
      console.log("Finalizando onSubmit, setIsSubmitting(false)");
      setIsSubmitting(false);
  }
};

  // Función para manejar la respuesta de la IA
  const handleImproveResult = (improvedData) => {
    console.log('Datos mejorados:', improvedData);
    
    try {
      // Extraer la descripción mejorada del formato estandarizado
      let descriptionText = '';
      
      if (typeof improvedData === 'string') {
        descriptionText = improvedData;
      } else if (improvedData && improvedData.data && improvedData.data.description) {
        descriptionText = improvedData.data.description;
      } else if (improvedData && improvedData.description) {
        descriptionText = improvedData.description;
      } else if (improvedData) {
        descriptionText = JSON.stringify(improvedData);
      }
      
      // Actualizar el campo de descripción
      if (descriptionText) {
        setValue('description', descriptionText, {
          shouldValidate: true,
          shouldDirty: true,
          shouldTouch: true
        });
        
        // Validar el campo después de actualizarlo
        trigger('description');
        
        // Mostrar confirmación
        Swal.fire({
          icon: 'success',
          title: '¡Texto mejorado!',
          text: 'La descripción ha sido mejorada con IA',
          timer: 1500,
          showConfirmButton: false
        });
      }
    } catch (error) {
      console.error('Error al aplicar mejora:', error);
    }
  };

  return (
    <div className={isEdit ? "form-container" : "form-box"}>
      <form className="form-create" onSubmit={handleSubmit(onSubmit)}>
        <h2>{isEdit ? "EDITAR ESTADO ACTUAL" : "CREAR ESTADO ACTUAL"}</h2>
        <div className="items">
          <label className="label-item">Descripción</label>
          <textarea
            rows="10"
            cols="50"
            {...register("description", {
              required: "Este campo es requerido",
              minLength: {
                value: 10,
                message: "La descripción debe tener al menos 10 caracteres",
              },
            })}
            disabled={isImproving}
            placeholder={isImproving ? "Mejorando descripción con IA..." : "Escribe una descripción o usa el botón de IA para mejorarla"}
            style={{
              backgroundColor: isImproving ? '#f5f5f5' : 'white',
              cursor: isImproving ? 'wait' : 'text'
            }}
          />
          {errors.description && (
            <p className="error-message">{errors.description.message}</p>
          )}
        </div>
        <div className="items">
          <label className="label-item">Fecha</label>
          <div className="date-input-wrapper">
            <input
              type="date"
              {...register("date", { required: "Este campo es requerido" })}
            />
            <span className="date-icon">&#x1F4C5;</span>
          </div>
          {errors.date && (
            <p className="error-message">{errors.date.message}</p>
          )}
        </div>
        <button className="button-forms" type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Procesando..." : isEdit ? "GUARDAR" : "CREAR"}
        </button>
        <button
          type="button"
          className="button-forms"
          onClick={() => setEditable(false)}
          disabled={isSubmitting}
        >
          CANCELAR
        </button>
        
        {/* Reemplazar el botón estático por el componente ImproveWithAIButton */}
        <ImproveWithAIButton
          className="button-forms"
          getValues={() => ({
            idForm,
            0: getValues("description") // Pasar la descripción en posición 0
          })}
          onResult={(data) => {
            setIsImproving(true);
            handleImproveResult(data);
            setIsImproving(false);
          }}
          disabled={isImproving}
        />
      </form>
    </div>
  );
};

// Definición correcta de PropTypes para ActualState
ActualState.propTypes = {
  actualStateId: PropTypes.string,
  challengeId: PropTypes.string.isRequired,
  setEditable: PropTypes.func.isRequired,
  isEdit: PropTypes.bool,
  // Hacemos setLoading opcional ya que parece que no siempre se está pasando
  setLoading: PropTypes.func,
};

// Valores por defecto para props opcionales
ActualState.defaultProps = {
  actualStateId: null,
  isEdit: false,
  setLoading: () => {}, // Función vacía como fallback para evitar errores
};

export default ActualState;