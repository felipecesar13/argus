package main

import (
	"log"

	"diff-processor/internal/server"
)

func main() {
	app := server.New()

	log.Println("Diff Processor running on :8081")

	if err := app.Listen(":8081"); err != nil {
		log.Fatal(err)
	}
}
