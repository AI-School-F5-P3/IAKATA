// import { useState, useEffect } from "react";
// import {
//   getActualState,
//   deleteActualState,
// } from "../../services/actualStateServices";
// import { useWebSocket } from "../../context/SocketContext";
// import { useSocket } from "../../utils/UseSocket";
// import "./css/SelectAll.css";
// import update from "../../assets/img/EditButton.svg";
// import ActualState from "../forms/ActualState";
// import delte from "../../assets/img/delete.svg";
// import more from "../../assets/img/Plus.svg";
// import Swal from "sweetalert2";

// const SelectAllActualState = ({ challengeId }) => {
//   const [actualStates, setActualStates] = useState(null);
//   const [editable, setEditable] = useState(false);
//   const [createActual, setCreateActual] = useState(false);
//   const [loading, setLoading] = useState(true);
//   const { WS_EVENTS, sendMessage } = useWebSocket();

//   useSocket(WS_EVENTS.ACTUAL_STATE, challengeId, (payload) => {
//     if (Array.isArray(payload)) {
//       const filteredState = payload.find(
//         (state) => state.challenge_id === challengeId
//       );
//       setActualStates(filteredState || null);
//     } else if (payload.challenge_id === challengeId) {
//       switch (payload.type) {
//         case "create":
//           setActualStates(payload);
//           setCreateActual(false);
//           break;
//         case "update":
//           setActualStates((prev) => ({ ...prev, ...payload }));
//           setEditable(false);
//           break;
//         case "delete":
//           setActualStates(null);
//           break;
//         default:
//           if (payload.challenge_id === challengeId) {
//             setActualStates(payload);
//           }
//       }
//     }
//     setLoading(false);
//   });

//   useEffect(() => {
//     let mounted = true;

//     const fetchActualState = async () => {
//       try {
//         setLoading(true);
//         const actualStateData = await getActualState();
//         if (mounted) {
//           const filteredState = actualStateData.find(
//             (state) => state.challenge_id === challengeId
//           );
//           setActualStates(filteredState || null);
//         }
//       } catch (error) {
//         console.error("Error fetching:", error);
//         if (mounted) {
//           Swal.fire({
//             icon: "error",
//             title: "Error",
//             text: "Error al cargar el estado actual",
//           });
//         }
//       } finally {
//         if (mounted) {
//           setLoading(false);
//         }
//       }
//     };

//     fetchActualState();

//     return () => {
//       mounted = false;
//     };
//   }, [challengeId]);

//   const handleDelete = async (id) => {
//     try {
//       const result = await Swal.fire({
//         title: "¿Estás seguro?",
//         text: "Esta acción no se puede deshacer",
//         icon: "warning",
//         showCancelButton: true,
//         confirmButtonColor: "#002661",
//         cancelButtonColor: "#ECF0F1",
//         confirmButtonText: "Sí, eliminar",
//         cancelButtonText: "Cancelar",
//         background: "#ECF0F1",
//         customClass: {
//           popup: "swal-custom-popup",
//           title: "swal-custom-title",
//           content: "swal-custom-content",
//           confirmButton: "swal-custom-confirm",
//           cancelButton: "swal-custom-cancel",
//         },
//       });

//       if (result.isConfirmed) {
//         await deleteActualState(id);
//         setActualStates(null);
//         sendMessage(WS_EVENTS.ACTUAL_STATE, {
//           message: "ActualState deleted",
//           id,
//           challenge_id: challengeId,
//           deleted: true,
//           timestamp: Date.now(),
//         });
//       }
//     } catch (error) {
//       console.error("Error deleting:", error);
//       Swal.fire({
//         title: "Error",
//         text: "No se pudo eliminar el estado actual",
//         icon: "error",
//         confirmButtonColor: "#002661",
//         background: "#ECF0F1",
//         customClass: {
//           popup: "swal-custom-popup",
//           title: "swal-custom-title",
//           content: "swal-custom-content",
//           confirmButton: "swal-custom-confirm",
//         },
//       });
//     }
//   };

//   return (
//     <div className="container-challenge">
//       <div className="titleAling">
//         <h3>
//           ESTADO ACTUAL
//           {!actualStates && (
//            <button title='Crear un nuevo estado objetivo' className='targetState' onClick={() => setCreateActual(true)}
//             >
//               <img src={more} className='createTargetState' />
//             </button>
//           )}
//         </h3>
//       </div>
//       {actualStates ? (
//         <div className="centered-table">
//           <table className="container-table">
//             <tbody>
//               <tr className="tr-table">
//                 <td className="title-table">Estado Actual ID</td>
//                 <td className="tr-table">{actualStates.id}</td>
//               </tr>
//               <tr className="tr-table">
//                 <td className="title-table">Descripción</td>
//                 <td className="tr-table description">
//                   {actualStates.description}
//                 </td>
//               </tr>
//               <tr className="tr-table">
//                 <td className="title-table">Fecha</td>
//                 <td className="tr-table">{actualStates.date}</td>
//               </tr>
//               <tr className="tr-table">
//                 <td className="title-table">Acciones</td>
//                 <td className="tr-table">
//                   <button
//                     title="Editar"
//                     className="CardActionButtonContainer"
//                     onClick={() => setEditable(true)}
//                   >
//                     <img src={update} alt="logo-update" className="edit" />
//                   </button>
//                   <button
//                     title="Eliminar"
//                     className="CardActionButtonContainer"
//                     onClick={() => handleDelete(actualStates.id)}
//                   >
//                     <img src={delte} alt="img-delete" className="delete" />
//                   </button>
//                 </td>
//               </tr>
//             </tbody>
//           </table>
//         </div>
//         ) : (
//             <p className="no-data">No hay estado actual</p>
//             )}
//       {(editable || createActual) && (
//         <ActualState
//           isEdit={editable}
//           actualStateId={actualStates?.id}
//           challengeId={challengeId}
//           setLoading={setLoading}
//           setEditable={editable ? setEditable : setCreateActual}
//         />
//       )}
//     </div>
//   );
// };

// export default SelectAllActualState;

import { useState, useEffect } from "react";
import {
  getActualState,
  deleteActualState,
} from "../../services/actualStateServices";
import { useWebSocket } from "../../context/SocketContext";
import { useSocket } from "../../utils/UseSocket";
import "./css/SelectAll.css";
import update from "../../assets/img/EditButton.svg";
import ActualState from "../forms/ActualState";
import delte from "../../assets/img/delete.svg";
import more from "../../assets/img/Plus.svg";
import Swal from "sweetalert2";

const SelectAllActualState = ({ challengeId }) => {
  const [actualStates, setActualStates] = useState(null);
  const [editable, setEditable] = useState(false);
  const [createActual, setCreateActual] = useState(false);
  const [loading, setLoading] = useState(true);
  const { WS_EVENTS, sendMessage } = useWebSocket();

  useSocket(
    WS_EVENTS.ACTUAL_STATE, 
    challengeId,
    (payload) => {
      if (Array.isArray(payload)) {
        const filteredState = payload.find(
          state => state.challenge_id === challengeId
        );
        setActualStates(filteredState || null);
      } else if (payload.deleted) {
          setActualStates(null);
      } else if (payload.challenge_id === challengeId) {
        switch (payload.type) {
          case "create":
            setActualStates(payload);
            setCreateActual(false);
            break;
          case "update":
            setActualStates((prev) => ({ ...prev, ...payload }));
            setEditable(false);
            break;
          default:
            setActualStates(payload);
        }
      }
      setLoading(false);
    }
  );

  useEffect(() => {
    let mounted = true;

    const fetchActualState = async () => {
      try {
        setLoading(true);
        const actualStateData = await getActualState();
        if (mounted) {
          const filteredState = actualStateData.find(
            (state) => state.challenge_id === challengeId
          );
          setActualStates(filteredState || null);
        }
      } catch (error) {
        console.error("Error fetching:", error);
        if (mounted) {
          Swal.fire({
            icon: "error",
            title: "Error",
            text: "Error al cargar el estado actual",
          });
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    fetchActualState();

    return () => {
      mounted = false;
    };
  }, [challengeId]);

  const handleDelete = async (id) => {
    try {
      const result = await Swal.fire({
        title: "¿Estás seguro?",
        text: "Esta acción no se puede deshacer",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#002661",
        cancelButtonColor: "#ECF0F1",
        confirmButtonText: "Sí, eliminar",
        cancelButtonText: "Cancelar",
        background: "#ECF0F1",
        customClass: {
          popup: "swal-custom-popup",
          title: "swal-custom-title",
          content: "swal-custom-content",
          confirmButton: "swal-custom-confirm",
          cancelButton: "swal-custom-cancel",
        },
      });

      if (result.isConfirmed) {
       const response = await deleteActualState(id);
        if (response) {
          sendMessage(WS_EVENTS.ACTUAL_STATE, {
            message: "ActualState deleted",
            id: id,
            deleted: true,
            timestamp: Date.now(),
          });
        }
      }
    } catch (error) {
      console.error("Error deleting:", error);
      Swal.fire({
        title: "Error",
        text: "No se pudo eliminar el estado actual",
        icon: "error",
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

  return (
    <div className="container-challenge">
      <div className="titleAling">
        <h3>
          ESTADO ACTUAL
          {!actualStates && (
           <button title='Crear un nuevo estado objetivo' className='targetState' onClick={() => setCreateActual(true)}
            >
              <img src={more} className='createTargetState' />
            </button>
          )}
        </h3>
      </div>
      {actualStates ? (
        <div className="centered-table">
          <table className="container-table">
            <tbody>
              <tr className="tr-table">
                <td className="title-table">Estado Actual ID</td>
                <td className="tr-table">{actualStates.id}</td>
              </tr>
              <tr className="tr-table">
                <td className="title-table">Descripción</td>
                <td className="tr-table description">
                  {actualStates.description}
                </td>
              </tr>
              <tr className="tr-table">
                <td className="title-table">Fecha</td>
                <td className="tr-table">{actualStates.date}</td>
              </tr>
              <tr className="tr-table">
                <td className="title-table">Acciones</td>
                <td className="tr-table">
                  <button
                    title="Editar"
                    className="CardActionButtonContainer"
                    onClick={() => setEditable(true)}
                  >
                    <img src={update} alt="logo-update" className="edit" />
                  </button>
                  <button
                    title="Eliminar"
                    className="CardActionButtonContainer"
                    onClick={() => handleDelete(actualStates.id)}
                  >
                    <img src={delte} alt="img-delete" className="delete" />
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        ) : (
            <p className="no-data">No hay estado actual</p>
            )}
      {(editable || createActual) && (
        <ActualState
          isEdit={editable}
          actualStateId={actualStates?.id}
          challengeId={challengeId}
          setLoading={setLoading}
          setEditable={editable ? setEditable : setCreateActual}
        />
      )}
    </div>
  );
};

export default SelectAllActualState;
