const socket = io.connect(window.location.host);
const title_p = $(".title");

socket.on('change_text', function(data){
    title_p.text(data["text"]);
});
