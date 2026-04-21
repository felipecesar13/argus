package server

import (
	"diff-processor/internal/handler"

	"github.com/gofiber/fiber/v3"
)

func New() *fiber.App {
	app := fiber.New(fiber.Config{
		AppName: "Diff Processor",
	})

	app.Get("/health", handler.Health)

	return app
}
