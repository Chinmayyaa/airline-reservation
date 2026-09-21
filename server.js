const express = require("express");

const app = express();

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use(express.static("public"));

let bookings = [
    {
        pnr: "A12345",
        passenger: "Arjun",
        seat: "12A",
        status: "Confirmed"
    },
    {
        pnr: "B12345",
        passenger: "Sneha",
        seat: "12B",
        status: "Confirmed"
    }
];

let waitlist = [];
let cancelledBookings = [];


// Home
app.get("/", (req, res) => {
    res.sendFile(__dirname + "/public/index.html");
});


// Get bookings
app.get("/api/bookings", (req, res) => {
    res.json(bookings);
});


// Get waitlist
app.get("/api/waitlist", (req, res) => {
    res.json(waitlist);
});


// Add to waitlist
app.post("/api/waitlist", (req, res) => {

    let name = req.body.name;
    let pnr = req.body.pnr;

    if (!name || !pnr) {
        return res.json({
            success: false,
            message: "Name and PNR are required"
        });
    }

    let existingBooking = bookings.find(function(booking) {
        return booking.pnr === pnr;
    });

    if (existingBooking) {
        return res.json({
            success: false,
            message: "PNR already exists"
        });
    }

    let existingWaitlist = waitlist.find(function(passenger) {
        return passenger.pnr === pnr;
    });

    if (existingWaitlist) {
        return res.json({
            success: false,
            message: "PNR already in waitlist"
        });
    }

    let passenger = {
        name: name,
        pnr: pnr,
        status: "Waitlisted",
        seat: "Not Assigned"
    };

    waitlist.push(passenger);

    res.json({
        success: true,
        message: "Passenger added to waitlist",
        passenger: passenger
    });
});


// Cancel booking
app.post("/api/cancel", (req, res) => {

    let pnr = req.body.pnr;

    let booking = bookings.find(function(item) {
        return item.pnr === pnr &&
               item.status === "Confirmed";
    });

    if (!booking) {
        return res.json({
            success: false,
            message: "Invalid PNR or booking already cancelled"
        });
    }

    booking.status = "Cancelled";

    cancelledBookings.push(booking);

    let promotedPassenger = null;

    if (waitlist.length > 0) {

        promotedPassenger = waitlist.shift();

        promotedPassenger.status = "Confirmed";
        promotedPassenger.seat = booking.seat;
    }

    res.json({
        success: true,
        message: "Booking cancelled successfully",
        booking: booking,
        promotedPassenger: promotedPassenger
    });
});


// Start server
app.listen(3000, function() {
    console.log("Server running at http://localhost:3000");
});