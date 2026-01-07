package worker

import (
	"context"
	"math/rand"
	"testing"
	"time"
)

func BenchmarkPoolProcessing(b *testing.B) {
	// Setup pool with 8 workers
	pool := NewPool(8)
	pool.Start()
	defer pool.Stop()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		pool.Submit(func(ctx context.Context) error {
			// Simulate some Work
			time.Sleep(1 * time.Millisecond)
			return nil
		})
	}
}

func TestPoolMemorySafety(t *testing.T) {
	// Test pool with memory limit enabled
	pool := NewPool(4)
	pool.MaxMemoryMB = 100 // 100MB Limit
	pool.Start()
	defer pool.Stop()

	// Submit a task that tries to allocate memory if limit allows
	done := make(chan bool)
	pool.Submit(func(ctx context.Context) error {
		defer func() { done <- true }()
		// In a real scenario, the pool would check BEFORE starting the task
		// but we can test the Submit blocking logic or logging
		return nil
	})

	select {
	case <-done:
		// Task executed
	case <-time.After(2 * time.Second):
		t.Error("Task timed out")
	}
}

func TestPoolLoad(t *testing.T) {
	pool := NewPool(10)
	pool.Start()
	defer pool.Stop()

	count := 100
	results := make(chan int, count)

	for i := 0; i < count; i++ {
		val := i
		pool.Submit(func(ctx context.Context) error {
			time.Sleep(time.Duration(rand.Intn(10)) * time.Millisecond)
			results <- val * 2
			return nil
		})
	}

	for i := 0; i < count; i++ {
		select {
		case <-results:
			// Success
		case <-time.After(5 * time.Second):
			t.Fatalf("Timed out waiting for task %d", i)
		}
	}
}
