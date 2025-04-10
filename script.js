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



{/* <script>
async function fetchSignedUrl(fileKey) {
    const response = await fetch(`https://seu-endpoint.amazonaws.com/prod?file_key=${fileKey}`);
    const data = await response.json();
    return data.url;
}

fetchSignedUrl('seu-arquivo.html').then(url => {
    // Utilize a URL assinada conforme necessário
    console.log('URL assinada:', url);
});
</script> */}
