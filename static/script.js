// Smart Parking System

document.addEventListener("DOMContentLoaded", function () {
    console.log("Smart Parking System Loaded");

    // Confirm before vehicle exit
    const exitButtons = document.querySelectorAll(".exit-btn");

    exitButtons.forEach(button => {
        button.addEventListener("click", function (e) {

            const confirmExit = confirm("Are you sure you want to exit this vehicle?");

            if (!confirmExit) {
                e.preventDefault();
            }

        });
    });

});