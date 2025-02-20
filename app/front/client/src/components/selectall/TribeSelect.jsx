import { useState, useEffect } from 'react';
import { getOneTribe, deleteTribe } from "../../services/tribeServices";
import { deleteProcess } from '../../services/processServices';
import './css/SelectAll.css';
import update from "../../assets/img/EditButton.svg";
import ProcessSelect from './ProcessSelect';
import Tribe from '../forms/Tribe';
import { getOneChallenge } from '../../services/challengeServices';
import delte from '../../assets/img/delete.svg';
import { useSocket } from '../../utils/UseSocket';
import { useWebSocket } from '../../context/SocketContext';
import Swal from 'sweetalert2';
import { useNavigate } from 'react-router-dom';

const TribeSelect = ({challengeId}) => {
    const [tribe, setTribe] = useState(null);
    const [editable, setEditable] = useState(false);
    const [loading, setLoading] = useState(false);  
    const { WS_EVENTS, sendMessage } = useWebSocket();
    const navigate = useNavigate();

    useSocket(
        WS_EVENTS.TRIBE,
        null,
        (payload) => {
            if (Array.isArray(payload)) {
                const filteredTribe = payload.find(t => t.process_id === tribe?.process_id);
                setTribe(filteredTribe || null);
            } else if (payload.deleted) {
                if (tribe && payload.id === tribe.id) {
                    setTribe(null);
                    navigate('/home/home');
                }
            } else {
                setTribe(payload);
            }
        }
    );
    
    useEffect(() => {
        const fetchProcess = async () => {
            try {
                const challengeData = await getOneChallenge(challengeId);  
                const tribeId = challengeData.data.tribe_id;  
                const tribeData = await getOneTribe(tribeId);
                setTribe(tribeData.data);
                setLoading(false);
            } catch (error) {
                console.error('Error:', error);
            }
        }
        fetchProcess();
    }, [challengeId, loading]);

    const handleDelete = async (tribeId) => {
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
                const tribeResponse = await deleteTribe(tribeId);
                const processResponse = await deleteProcess(tribe.process_id);
            
                if (tribeResponse.status === 200 && processResponse.status === 200) {         
                        sendMessage(WS_EVENTS.TRIBE, {
                            id: tribeId,
                            deleted: true,
                            timestamp: Date.now()
                        });
                        
                        sendMessage(WS_EVENTS.PROCESS, {
                            id: tribe.process_id,
                            deleted: true,
                            timestamp: Date.now()
                        });
                        
                        setTribe(null);
                        setLoading(true);
            }
        }
        } catch (error) {
            Swal.fire({
                title: 'Error',
                text: error.response?.data?.message || 'No se pudo eliminar la tribu',
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
        <div className='container-challenge'>
            {tribe && (
                <>
                <ProcessSelect processId={tribe.process_id}/>
                    <h3>TRIBU</h3>
                    <div className="centered-table">
                        <table className='container-table'>
                                    <tbody key={tribe.id}>
                                        <tr className='tr-table'>
                                            <td className='title-table'>Tribu ID</td>
                                            <td className='tr-table'>{tribe.id}</td>
                                        </tr>
                                        <tr className="tr-table">
                                            <td className='title-table'>Nombre de la tribu</td>
                                            <td className='tr-table'>{tribe.name_tribe}</td>
                                        </tr>
                                        <tr className="tr-table">
                                            <td className='title-table'>Miembro de la tribu</td>
                                            <td className='tr-table'>{tribe.team_members}</td>
                                        </tr> 
                                        <tr className="tr-table">
                                            <td className='title-table'>Proceso ID</td>
                                            <td className='tr-table'>{tribe.process_id}</td>
                                        </tr> 
                                        <tr className="tr-table">
                                            <td className='title-table'>Acciones</td>
                                            <td className='tr-table'>
                                                <button title='Editar' className='CardActionButtonContainer' onClick={() => setEditable(true)}>
                                                    <img src={update} alt="logo-update" className='edit' />
                                                </button>
                                                {/* <button title='Eliminar' className='CardActionButtonContainer' onClick={() => {deleteTribe(tribe.id), setLoading(true)}}> */}
                                                <button title='Eliminar' className='CardActionButtonContainer' onClick={() => handleDelete(tribe.id)}>
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
                <Tribe isEdit={true} tribeId={tribe.id} setLoading={setLoading} setEditable={setEditable}/>
            )}
        </div>
    );
};

export default TribeSelect ;

