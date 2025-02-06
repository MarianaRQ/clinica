function formatDate(dateString) {
    const options = { year: 'numeric', month: '2-digit', day: '2-digit' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

$(document).ready(function () {
    $('#searchForm').on('submit', function (e) {
        e.preventDefault(); // Prevenir el comportamiento predeterminado del formulario

        const searchTerm = $('#searchInput').val(); // Obtener el valor del input

        $.ajax({
            url: '/search', // URL del backend
            type: 'POST', // Método POST
            data: { search: searchTerm }, // Enviar el término de búsqueda
            success: function (data) {
                const tableBody = $('#treatmentTableBody');
                tableBody.empty(); // Limpiar la tabla

                if (data.length === 0) {
                    tableBody.append('<tr><td colspan="7" class="text-center">No se encontraron resultados</td></tr>');
                } else {
                    data.forEach(item => {
                        tableBody.append(`
                            <tr>
                                <td>${item.Id}</td>
                                <td>${item.Nombre}</td>
                                <td>${formatDate(item.Fecha_Inicio)}</td>
                                <td>${item.paciente}</td>
                                <td>${item.Medico}</td>
                                <td>
                                    <button class="btn btn-primary btn-sm boton" data-bs-toggle="modal"
                                        data-bs-target="#modal-edit-${item.Id}">
                                        Editar
                                    </button>
                                </td>
                                <td>
                                    <a href="/tratamiento/delete/${item.Id}" class="btn btn-danger btn-sm">Eliminar</a>
                                </td>
                            </tr>
                        `);
                    });
                }
            },
            error: function () {
                alert('Hubo un error al realizar la búsqueda.');
            }
        });
    });

    // Formatea las fechas en la tabla inicial
    $('#treatmentTableBody tr').each(function() {
        const dateCell = $(this).find('td').eq(2); // Suponiendo que la fecha es la tercera columna
        const formattedDate = formatDate(dateCell.text());
        dateCell.text(formattedDate);
    });
});
