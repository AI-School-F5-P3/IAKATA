import { useState, useEffect } from "react";
import { getOneProcess, deleteProcess } from "../../services/processServices";
import "./css/SelectAll.css";
import update from "../../assets/img/EditButton.svg";
import Process from "../forms/Process";
import { getChallenge } from "../../services/challengeServices";
import ChallengeSelect from "../ChallengeSelect/ChallengeSelect";
import delte from '../../assets/img/delete.svg';
import { useSocket } from '../../utils/UseSocket';
import { useWebSocket } from '../../context/SocketContext';
import Swal from 'sweetalert2';

const ProcessSelect = ({ processId }) => {
  const [process, setProcess] = useState(null);
  const [editable, setEditable] = useState(false);
  const [loading, setLoading] = useState(false);
  const [challenges, setChallenges] = useState([]);
  const [selectedChallengeId, setSelectedChallengeId] = useState(null);
  const { WS_EVENTS, sendMessage } = useWebSocket();

  useSocket(
    WS_EVENTS.PROCESS,
    processId,
    (payload) => {
      if (Array.isArray(payload)) {
        setProcess(payload.find(p => p.id === processId)?.data);
      } else if (payload.deleted) {
        setProcess(null);
      } else if (payload.id === processId) {
        setProcess(payload);
      }
    }
  );
  
  useEffect(() => {
    const fetchProcess = async () => {
      try {
        const processData = await getOneProcess(processId);
        setProcess(processData.data);
        setLoading(false);
      } catch (error) {
        console.error("Error:", error);
      }
    };
    fetchProcess();
  }, [processId, loading]);

  useEffect(() => {
    const fetchChallenges = async () => {
      try {
        const challengesData = await getChallenge();
        setChallenges(challengesData);
      } catch (error) {
        console.error('Error fetching Challenges:', error);
      }
    };

    fetchChallenges();
  }, []);

  const handleDelete = async (id) => {
    try {
      const result = await Swal.fire({
        title: '¿Estás seguro?',
        text: "Esta acción no se puede deshacer",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#002661',
        cancelButtonColor: '#ECF0F1',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar',
        background: '#ECF0F1',
        customClass: {
          popup: 'swal-custom-popup',
          title: 'swal-custom-title',
          content: 'swal-custom-content',
          confirmButton: 'swal-custom-confirm',
          cancelButton: 'swal-custom-cancel'
        }
      });

      if (result.isConfirmed) {
        const response = await deleteProcess(id);
        if (response) {
          sendMessage(WS_EVENTS.PROCESS, {
            id: id,
            deleted: true,
            timestamp: Date.now()
          });
          setLoading(true);
        }
      }
    } catch (error) {
      Swal.fire({
        title: 'Error',
        text: error.response?.data?.message || 'No se pudo eliminar el proceso',
        icon: 'error',
        customClass: {
          popup: 'swal-custom-popup',
          title: 'swal-custom-title',
          content: 'swal-custom-content',
          confirmButton: 'swal-custom-confirm'
        }
      });
    }
  };

  return (
    <div className="container-challenge marginNavbar">
      <ChallengeSelect 
        challenges={challenges} 
        selectedChallengeId={selectedChallengeId} 
        onSelectChange={(id) => setSelectedChallengeId(id)}
      />
      {process && (
        <>
          <h3>PROCESO</h3>
          <div className="centered-table">
            <table className="container-table">
              <tbody key={process.id}>
                <tr className="tr-table">
                  <td className="title-table">Proceso ID</td>
                  <td className="tr-table">{process.id}</td>
                </tr>
                <tr className="tr-table">
                  <td className="title-table">Descripcion</td>
                  <td className="tr-table">{process.description}</td>
                </tr>
                <tr className="tr-table">
                  <td className="title-table">Acciones</td>
                  <td className="tr-table">
                    <button
                      title='Editar' className='CardActionButtonContainer'
                      onClick={() => setEditable(true)}
                    >
                      <img
                      className='edit'
                        src={update}
                        alt="logo-update"
                      />
                    </button>
                    {/* <button title='Eliminar' className='CardActionButtonContainer' onClick={() => {deleteProcess(process.id), setLoading(true)}}> */}
                    <button title='Eliminar' className='CardActionButtonContainer' onClick={() => {handleDelete(process.id)}}>
                    <img src={delte} alt="img-delete" className='delete' />
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </>
      )}
      {editable && (
        <Process
          isEdit={true}
          processId={processId}
          setLoading={setLoading}
          setEditable={setEditable}
        />
      )}
    </div>
  );
};

export default ProcessSelect;

