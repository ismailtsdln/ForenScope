package worker

import (
	"context"
	"log"
	"runtime"
	"sync"
	"time"
)

// Task represents a unit of work.
type Task func(ctx context.Context) error

// Pool manages a pool of workers to execute tasks concurrently.
type Pool struct {
	taskQueue   chan Task
	wg          sync.WaitGroup
	quit        chan struct{}
	maxWorker   int
	ctx         context.Context
	cancel      context.CancelFunc
	MaxMemoryMB uint64 // New: Memory limit in MB
}

// NewPool creates a new worker pool.
func NewPool(maxWorker int) *Pool {
	ctx, cancel := context.WithCancel(context.Background())
	return &Pool{
		taskQueue: make(chan Task, maxWorker*10),
		quit:      make(chan struct{}),
		maxWorker: maxWorker,
		ctx:       ctx,
		cancel:    cancel,
	}
}

// Start spins up the workers.
func (p *Pool) Start() {
	for i := 0; i < p.maxWorker; i++ {
		p.wg.Add(1)
		go func(workerID int) {
			defer p.wg.Done()
			for {
				select {
				case task := <-p.taskQueue:
					if task == nil {
						continue
					}
					// Execute task
					if err := task(p.ctx); err != nil {
						// log.Printf("Worker %d: Task error: %v", workerID, err)
					}
				case <-p.quit:
					return
				case <-p.ctx.Done():
					return
				}
			}
		}(i)
	}
}

// checkMemory returns true if memory usage is within limits.
func (p *Pool) checkMemory() bool {
	if p.MaxMemoryMB == 0 {
		return true
	}
	var m runtime.MemStats
	runtime.ReadMemStats(&m)
	usageMB := m.Alloc / 1024 / 1024
	return usageMB < p.MaxMemoryMB
}

// Submit enqueues a task, respecting memory limits if set.
func (p *Pool) Submit(t Task) {
	// Block if memory limit is exceeded
	for !p.checkMemory() {
		log.Printf("Memory limit exceeded (%d MB). Waiting...", p.MaxMemoryMB)
		select {
		case <-time.After(500 * time.Millisecond):
			// Check again
		case <-p.quit:
			return
		case <-p.ctx.Done():
			return
		}
	}

	select {
	case p.taskQueue <- t:
	case <-p.quit:
		return
	case <-p.ctx.Done():
		return
	}
}

// Stop signals all workers to stop.
func (p *Pool) Stop() {
	p.cancel()
	close(p.quit)
	p.wg.Wait()
	log.Println("Worker pool stopped")
}
