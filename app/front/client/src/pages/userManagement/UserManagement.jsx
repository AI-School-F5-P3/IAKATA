import { useState, useEffect, useCallback } from "react";
import { useUserContext } from "../../context/UserContext";
import Swal from "sweetalert2";
import "./useManager.css";
import { getAllUsers, updateUser } from "../../services/userServices";

const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState("all");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const { user } = useUserContext();

  const fetchUsers = useCallback(async () => {
    try {
      setLoading(true);
      const response = await getAllUsers({
        filter,
        page,
        limit: 10,
      });

      if (response.success) {
        setUsers(response.data.users);
        setTotalPages(response.data.totalPages);
      }
    } catch (error) {
      console.error("Error fetching users:", error);
      Swal.fire({
        icon: "error",
        title: "Error",
        text: "Error al cargar los usuarios",
        customClass: {
          popup: "user-management-dialog",
          confirmButton: "user-management-confirm",
        },
      });
    } finally {
      setLoading(false);
    }
  }, [filter, page]);

  useEffect(() => {
    if (user?.rol === "admin") {
      fetchUsers();
    }
  }, [fetchUsers, user?.rol]);

  const handleNameChange = async (userId, currentName) => {
    try {
      const { value: newName } = await Swal.fire({
        title: "Editar Nombre",
        input: "text",
        inputLabel: "Nuevo nombre",
        inputValue: currentName,
        showCancelButton: true,
        confirmButtonText: "Guardar",
        cancelButtonText: "Cancelar",
        customClass: {
          popup: "user-management-dialog",
          confirmButton: "user-management-confirm",
          cancelButton: "user-management-cancel",
          input: "user-management-input"
        }
      });
  
      if (newName && newName !== currentName) {
        await updateUser(userId, { name: newName });
        await fetchUsers();
        Swal.fire({
          title: "¡Cambio exitoso!",
          text: "El nombre ha sido actualizado.",
          icon: "success",
          customClass: {
            popup: "user-management-dialog",
            confirmButton: "user-management-confirm"
          }
        });
      }
    } catch (error) {
      Swal.fire({
        icon: "error",
        title: "Error",
        text: "Error al actualizar el nombre",
        customClass: {
          popup: "user-management-dialog",
          confirmButton: "user-management-confirm"
        }
      });
    }
  };
  

  const handleRoleChange = async (userId, newRole) => {
    try {
      const result = await Swal.fire({
        title: "¿Estás seguro?",
        text: `¿Deseas cambiar el rol del usuario a ${newRole}?`,
        icon: "warning",
        showCancelButton: true,
        confirmButtonText: "Sí, cambiar",
        cancelButtonText: "Cancelar",
        customClass: {
          popup: "user-management-dialog",
          confirmButton: "user-management-confirm",
          cancelButton: "user-management-cancel",
        },
      });

      if (result.isConfirmed) {
        await updateUser(userId, { rol: newRole });
        await fetchUsers();
        Swal.fire({
          title: "¡Cambio exitoso!",
          text: "El rol del usuario ha sido actualizado.",
          icon: "success",
          customClass: {
            popup: "user-management-dialog",
            confirmButton: "user-management-confirm",
          },
        });
      }
    } catch (error) {
      Swal.fire({
        icon: "error",
        title: "Error",
        text: "Error al actualizar el rol del usuario",
        customClass: {
          popup: "user-management-dialog",
          confirmButton: "user-management-confirm",
        },
      });
    }
  };

  const handleEmailChange = async (userId, currentEmail) => {
    try {
      const { value: newEmail } = await Swal.fire({
        title: "Editar Email",
        input: "email",
        inputLabel: "Nuevo email",
        inputValue: currentEmail,
        showCancelButton: true,
        confirmButtonText: "Guardar",
        cancelButtonText: "Cancelar",
        customClass: {
          popup: "user-management-dialog",
          confirmButton: "user-management-confirm",
          cancelButton: "user-management-cancel",
          input: "user-management-input",
        },
        inputValidator: (value) => {
          if (!value) return "El email no puede estar vacío";
          const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
          if (!emailRegex.test(value)) {
            return "Por favor, introduce un email válido";
          }
        },
      });

      if (newEmail && newEmail !== currentEmail) {
        await updateUser(userId, { email: newEmail });
        await fetchUsers();
        Swal.fire({
          title: "¡Cambio exitoso!",
          text: "El email ha sido actualizado.",
          icon: "success",
          customClass: {
            popup: "user-management-dialog",
            confirmButton: "user-management-confirm",
          },
        });
      }
    } catch (error) {
      Swal.fire({
        icon: "error",
        title: "Error",
        text: "Error al actualizar el email",
        customClass: {
          popup: "user-management-dialog",
          confirmButton: "user-management-confirm",
        },
      });
    }
  };

  const filteredUsers = users.filter((u) => {
    if (filter === "active") return u.isActive;
    if (filter === "inactive") return !u.isActive;
    return true;
  });

  if (user?.rol !== "admin") {
    return (
      <div className="container-challenge marginNavbar">
        <h3>Acceso Denegado</h3>
        <p>No tienes permisos para ver esta página</p>
      </div>
    );
  }

  return (
    <div className="user-management-container">
      <h3 className="user-management-title">GESTIÓN DE USUARIOS</h3>

      <div className="user-filter-container">
        <select
          className="user-filter-select"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        >
          <option value="all">Todos los usuarios</option>
          <option value="active">Usuarios activos</option>
          <option value="inactive">Usuarios inactivos</option>
        </select>
      </div>

      <div className="user-table-container">
        <table className="user-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Nombre</th>
              <th>Email</th>
              <th>Rol</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {filteredUsers.map((user) => (
              <tr key={user.id}>
                <td>{user.id}</td>
                <td
                  className="user-name-cell"
                  onClick={() => handleNameChange(user.id, user.name)}
                >
                  {user.name}
                  <span className="edit-icon">✎</span>
                </td>
                <td
                  className="user-email-cell"
                  onClick={() => handleEmailChange(user.id, user.email)}
                >
                  {user.email}
                  <span className="edit-icon">✎</span>
                </td>{" "}
                <td>{user.rol}</td>
                <td
                  className={
                    user.isActive
                      ? "user-status-active"
                      : "user-status-inactive"
                  }
                >
                  {user.isActive ? "Activo" : "Inactivo"}
                </td>
                <td>
                  <button
                    className="user-action-button"
                    onClick={() =>
                      handleRoleChange(
                        user.id,
                        user.rol === "admin" ? "user" : "admin"
                      )
                    }
                  >
                    {user.rol === "admin" ? "Hacer Usuario" : "Hacer Admin"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="user-pagination">
        <button
          className="pagination-button"
          onClick={() => setPage((p) => Math.max(1, p - 1))}
          disabled={page === 1}
        >
          Anterior
        </button>
        <span className="pagination-info">
          Página {page} de {totalPages}
        </span>
        <button
          className="pagination-button"
          onClick={() => setPage((p) => p + 1)}
          disabled={page >= totalPages}
        >
          Siguiente
        </button>
      </div>
    </div>
  );
};

export default UserManagement;