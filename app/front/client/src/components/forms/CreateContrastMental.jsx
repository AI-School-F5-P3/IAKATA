import { useState, useEffect, useCallback } from "react";
import PropTypes from "prop-types";
import { useForm } from "react-hook-form";
import {
  postMentalContrast,
  getOneMentalContrast,
  updateMentalContrast,
} from "../../services/mentalContrastServices";
import "./css/Forms.css";
import { useWebSocket } from "../../context/SocketContext";
import Swal from "sweetalert2";

const ContrastMental = ({
  editMentalId,
  editTargetId,
  setLoading,
  setEditMental,
  setEditContrast,
  isEdit = false,
}) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    reset,
    watch,
  } = useForm();
  const [mentalContrastData, setMentalContrastData] = useState({});
  const { WS_EVENTS, sendMessage } = useWebSocket();

  const getCurrentDate = useCallback(() => {
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, "0");
    const day = String(today.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
  }, []);

  useEffect(() => {
    if (isEdit && editMentalId) {
      const fetchData = async () => {
        try {
          const response = await getOneMentalContrast(editMentalId);
          const data = response.data;
          setMentalContrastData(data);
          setValue("points", data.points);
          setValue("evaluation_date", data.evaluation_date);
        } catch (error) {
          console.error("Error:", error);
          Swal.fire({
            icon: "error",
            title: "Error",
            text: "Error al cargar el contraste mental",
            confirmButtonColor: "#002661",
            background: "#ECF0F1",
            customClass: {
              popup: "swal-custom-popup",
              title: "swal-custom-title",
              content: "swal-custom-content",
              confirmButton: "swal-custom-confirm",
            },
          });
        }
      };
      fetchData();
    } else {
      setValue("evaluation_date", getCurrentDate());
    }
  }, [editMentalId, setValue, isEdit, getCurrentDate]);

  const onSubmit = async (data) => {
    try {
      if (!data.points || !data.evaluation_date) {
        Swal.fire({
          icon: "error",
          title: "Error",
          text: "Todos los campos son requeridos",
          customClass: {
            popup: "swal-custom-popup",
            title: "swal-custom-title",
            content: "swal-custom-content",
            confirmButton: "swal-custom-confirm",
          },
        });
        return;
      }

      const formData = {
        points: parseInt(data.points),
        evaluation_date: data.evaluation_date,
        target_state_id: String(
          isEdit ? mentalContrastData.target_state_id : editTargetId
        ),
      };

      if (
        !formData.points ||
        !formData.evaluation_date ||
        !formData.target_state_id
      ) {
        throw new Error("Datos incompletos");
      }

      const response = await (isEdit
        ? updateMentalContrast(editMentalId, formData)
        : postMentalContrast(formData));

        if (response && response.id) {
            await Swal.fire({
                icon: "success",
                title: "¡Éxito!",
                text: isEdit ? "Contraste mental actualizado correctamente" : "Contraste mental creado correctamente", // Corregir el texto
                confirmButtonColor: "#002661",
                background: "#ECF0F1",
                customClass: {
                    popup: "swal-custom-popup",
                    title: "swal-custom-title",
                    content: "swal-custom-content",
                    confirmButton: "swal-custom-confirm",
                }
            });
        
            sendMessage(WS_EVENTS.MENTAL_CONTRAST, {
                ...response,
                target_state_id: formData.target_state_id,
                type: isEdit ? "update" : "create",
                timestamp: Date.now()
            });
        
            setLoading(true);
            isEdit ? setEditMental(false) : setEditContrast(false); 
            handleClose();
        }
    } catch (error) {
      console.error("Error:", error);
      Swal.fire({
        title: "Error",
        text: error.message || "Error al guardar el contraste mental",
        icon: "error",
        customClass: {
          popup: "swal-custom-popup",
          title: "swal-custom-title",
          content: "swal-custom-content",
          confirmButton: "swal-custom-confirm",
        },
      });
    }
  };

  const validateEvaluationDate = (value) => {
    if (!isEdit) {
      const currentDate = getCurrentDate();
      if (value !== currentDate) {
        return `La fecha de evaluación debe coincidir con el día actual (${currentDate})`;
      }
    }
    return true;
  };

const handleClose = useCallback(() => {
    if (!isEdit && !editMentalId) {
        reset({
            points: "",
            evaluation_date: getCurrentDate(),
        });
    }
    setMentalContrastData({});
    isEdit ? setEditMental(false) : setEditContrast(false);
}, [reset, setEditMental, setEditContrast, isEdit, editMentalId, getCurrentDate]);

  return (
    <div className="form-container">
      <form className="form-create" onSubmit={handleSubmit(onSubmit)}>
        <h2>{isEdit ? "EDITAR" : "CREAR"} CONTRASTE MENTAL</h2>
        <div className="items">
          <label className="label-item">Puntuación</label>
          <input
            type="number"
            min="1"
            max="10"
            {...register("points", {
              required: "La puntuación es requerida",
              min: { value: 1, message: "La puntuación mínima es 1" },
              max: { value: 10, message: "La puntuación máxima es 10" },
            })}
          />
          {errors.points && (
            <p className="error-message">{errors.points.message}</p>
          )}
        </div>
        <div className="items">
          <label className="label-item">Fecha de evaluación:</label>
          <div className="date-input-wrapper">
            <input
              type="date"
              {...register("evaluation_date", {
                required: true,
                validate: validateEvaluationDate,
              })}
            />
            <span className="date-icon">&#x1F4C5;</span>
          </div>
          {errors.evaluation_date && (
            <p className="error-message">{errors.evaluation_date.message}</p>
          )}
        </div>
        <button
          className="button-forms"
          type="submit"
          disabled={!watch("points") || !watch("evaluation_date")}
        >
          {isEdit ? "Guardar" : "Enviar"}
        </button>
        <button type="button" className="button-forms" onClick={handleClose}>
          Cerrar
        </button>
      </form>
    </div>
  );
};
ContrastMental.propTypes = {
  editMentalId: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  editTargetId: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  setLoading: PropTypes.func.isRequired,
  setEditMental: PropTypes.func.isRequired,
  setEditContrast: PropTypes.func.isRequired,
  isEdit: PropTypes.bool,
};

export default ContrastMental;