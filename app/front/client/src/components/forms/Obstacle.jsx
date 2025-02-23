import { useState, useEffect, useCallback } from "react";
import PropTypes from "prop-types";
import { useForm } from "react-hook-form";
import {
  postObstacle,
  uploadImage,
  getOneObstacle,
  updateObstacle,
} from "../../services/obstacleServices";
import "./css/Forms.css";
import { useWebSocket } from "../../context/SocketContext";
import Swal from "sweetalert2";

import ImproveWithAIButton from '../buttonIa/ImproveWithAIButton';

const Obstacle = ({
  editObstacleId,
  editTargetId,
  setLoading,
  setEditObstacle,
  isEdit = false,
}) => {
  const {
    getValues,
    handleSubmit,
    register,
    formState: { errors },
    setValue,
    reset,
    watch,
  } = useForm();
  const [imageUrl, setImageUrl] = useState("");
  const [obstacleData, setObstacleData] = useState(null);
  const { WS_EVENTS, sendMessage } = useWebSocket();

  const idForm = "OB";

  useEffect(() => {
    const fetchData = async () => {
      if (isEdit && editObstacleId) {
        try {
          const data = await getOneObstacle(editObstacleId);
          setObstacleData(data);
          setValue("description", data.description);
          setImageUrl(data.image);
        } catch (error) {
          console.error("Error fetching obstacle:", error);
          Swal.fire("Error", "No se pudo cargar el obstáculo", "error");
        }
      }
    };
    fetchData();
  }, [isEdit, editObstacleId, setValue]);

  const onSubmit = async (data) => {
    try {
      if (!data.description) {
        Swal.fire({
          icon: "error",
          title: "Error",
          text: "No se pudo cargar el obstáculo",
          confirmButtonColor: "#002661",
          background: "#ECF0F1",
          customClass: {
            popup: "swal-custom-popup",
            title: "swal-custom-title",
            content: "swal-custom-content",
            confirmButton: "swal-custom-confirm",
          },
        });
        return;
      }

      let imageURL = imageUrl;
      if (data.image && data.image[0]) {
        const imageData = new FormData();
        imageData.append("file", data.image[0]);
        imageData.append("upload_preset", "LeanKata");
        const responseImage = await uploadImage(imageData);
        imageURL = responseImage.secure_url;
      }

      const formData = {
        description: data.description.trim(),
        image: imageURL || "",
        target_state_id: String(
          isEdit ? obstacleData.target_state_id : editTargetId
        ),
      };

      if (!formData.description || !formData.target_state_id) {
        throw new Error("Datos incompletos");
      }
      const response = await (isEdit
        ? updateObstacle(editObstacleId, formData)
        : postObstacle(formData));

      if (response && response.id) {
        await Swal.fire({
          icon: "success",
          title: "¡Éxito!",
          text: isEdit
            ? "Obstáculo actualizado correctamente"
            : "Obstáculo creado correctamente",
          confirmButtonColor: "#002661",
          background: "#ECF0F1",
          customClass: {
            popup: "swal-custom-popup",
            title: "swal-custom-title",
            content: "swal-custom-content",
            confirmButton: "swal-custom-confirm",
          },
        });

        sendMessage(WS_EVENTS.OBSTACLE, {
          ...response,
          target_state_id: formData.target_state_id,
          type: isEdit ? "update" : "create",
          timestamp: Date.now(),
        });

        setLoading(true);
        setEditObstacle(false);
        handleClose();
      }
    } catch (error) {
      console.error("Form submission error:", error);
      Swal.fire({
        icon: "error",
        title: "Error",
        text: error.message || "No se pudo guardar el obstáculo",
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

  const handleClose = useCallback(() => {
    if (!isEdit && !editObstacleId) {
      reset({
        description: "",
        image: null,
      });
    }
    setImageUrl("");
    setObstacleData(null);
    setEditObstacle(false);
  }, [reset, setEditObstacle, isEdit, editObstacleId]);
  
  const handleImproveResult = (improvedData) => {
    console.log('Datos mejorados:', improvedData);
    setValue('description', improvedData.description); // Actualiza el campo de descripción
    };

  return (
    <div className="form-container">
      <form className="form-create" onSubmit={handleSubmit(onSubmit)}>
        <h2>{isEdit ? "EDITAR" : "CREAR"} OBSTÁCULO</h2>
        <div className="items">
          <label className="label-item">Descripción</label>
          <textarea
            rows="10"
            cols="50"
            {...register("description", {
              required: "La descripción es requerida",
            })}
          />
          {errors.description && (
            <p className="error-message">{errors.description.message}</p>
          )}
        </div>
        <div className="items">
          <label className="label-item">Imagen:</label>
          <input className="button-image" type="file" {...register("image")} />
          {imageUrl && (
            <img
              src={imageUrl}
              alt="Preview"
              className="image-preview"
              style={{ maxWidth: "200px" }}
            />
          )}
        </div>
        <button
          className="button-forms"
          type="submit"
          disabled={!watch("description")}
        >
          {isEdit ? "Guardar" : "Enviar"}
        </button>
        <button type="button" className="button-forms" onClick={handleClose}>
          Cerrar
        </button>
        <ImproveWithAIButton
          className="button-forms"
          getValues={() => ({
              idForm,
              ...getValues(["description"])
          })}
          onResult={handleImproveResult} 
        />
      </form>
    </div>
  );
};
Obstacle.propTypes = {
  editObstacleId: PropTypes.string,
  editTargetId: PropTypes.string,
  setLoading: PropTypes.func.isRequired,
  setEditObstacle: PropTypes.func.isRequired,
  isEdit: PropTypes.bool,
};

export default Obstacle;