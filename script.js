document.getElementById('uploadForm').addEventListener('submit', async (event) => {
    event.preventDefault();
    const file = document.getElementById('fileInput').files[0];
    if (file) {
        const response = await fetch('https://https://7kd3205lna.execute-api.us-east-1.amazonaws.com/default/upload_file_to_s3_url_assigned', {
            method: 'POST',
            body: file
        });
        const result = await response.json();
        alert(result.message);
    }
});


// Funções que serão usadas para fazer o upload do arquivo


// 1. Requisição para obter URL pré-assinada (JSON):

// Obter URL pré-assinada
fetch('https://seu-endpoint-api-gateway', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        fileName: 'documento.pdf',
        contentType: 'application/pdf',
        maxSize: 10485760
    })
})
.then(response => response.json())
.then(data => {
    if (data.statusCode === 200) {
        // Sucesso - temos a URL pré-assinada
        const presignedUrl = data.body.url;
        console.log('URL pré-assinada:', presignedUrl);
    } else {
        // Erro
        console.error('Erro:', data.body.error);
    }
})
.catch(error => console.error('Erro na requisição:', error));

// 2. Requisição para fazer o upload do arquivo (PUT):
// Upload do arquivo
const file_upload_1 = document.getElementById('fileInput').files[0];
const formData = new FormData();
formData.append('file', file_upload_1);

fetch(presignedUrl.url, {
    method: 'POST',
    body: formData
})
.then(response => response.text())
.then(data => {
    console.log('Upload concluído:', data);
})
.catch(error => console.error('Erro no upload:', error));

// 3. Requisição para obter o arquivo (GET):
// Função para obter URL pré-assinada
function getPresignedUrl(fileName, contentType, maxSize) {
    return fetch('https://seu-endpoint-api-gateway', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            fileName,
            contentType,
            maxSize
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.statusCode === 200) {
            return data.body.url;
        } else {
            throw new Error(data.body.error);
        }
    });
}

// Função para fazer upload do arquivo
function uploadFile(file, presignedUrl) {
    const formData = new FormData();
    formData.append('file', file);

    return fetch(presignedUrl.url, {
        method: 'POST',
        body: formData
    })
    .then(response => response.text())
    .then(data => {
        console.log('Upload concluído:', data);
        return data;
    });
}

// Uso das funções
const file_upload = document.getElementById('fileInput').files[0];

getPresignedUrl(file_upload.name, file_upload.type, file_upload.size)
    .then(presignedUrl => {
        return uploadFile(file_upload, presignedUrl);
    })
    .then(result => {
        console.log('Processo completo:', result);
    })
    .catch(error => {
        console.error('Erro:', error);
    });


// 4. Exemplo com async/await:
async function uploadFileWithPresignedUrl(file) {
    try {
        // Obter URL pré-assinada
        const presignedUrlResponse = await fetch('https://seu-endpoint-api-gateway', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                fileName: file.name,
                contentType: file.type,
                maxSize: file.size
            })
        });
        
        const presignedUrlData = await presignedUrlResponse.json();
        
        if (presignedUrlData.statusCode !== 200) {
            throw new Error(presignedUrlData.body.error);
        }

        // Fazer upload do arquivo
        const formData = new FormData();
        formData.append('file', file);

        const uploadResponse = await fetch(presignedUrlData.body.url.url, {
            method: 'POST',
            body: formData
        });

        const uploadResult = await uploadResponse.text();
        console.log('Upload concluído:', uploadResult);
        return uploadResult;

    } catch (error) {
        console.error('Erro no processo:', error);
        throw error;
    }
}

// Uso da função
document.getElementById('uploadForm').addEventListener('submit', async (event) => {
    event.preventDefault();
    const file = document.getElementById('fileInput').files[0];
    
    try {
        await uploadFileWithPresignedUrl(file);
        alert('Upload concluído com sucesso!');
    } catch (error) {
        alert('Erro no upload: ' + error.message);
    }
});