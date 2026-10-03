package com.example.demo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.Map;
import java.util.List;

@SpringBootApplication
@RestController
public class Application {

    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }

    @GetMapping("/")
    public Map<String, String> root() {
        return Map.of("service", "BillingService", "status", "active");
    }

    @GetMapping("/health")
    public Map<String, String> health() {
        return Map.of("status", "UP", "database", "PostgreSQL Connected");
    }

    @GetMapping("/api/invoices")
    public List<Map<String, Object>> getInvoices() {
        return List.of(
            Map.of("id", "INV-1001", "amount", 1250.00, "status", "PAID"),
            Map.of("id", "INV-1002", "amount", 430.50, "status", "DUE")
        );
    }
}
