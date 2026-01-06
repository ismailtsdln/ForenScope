package worker

import (
	"context"
	"log"
	"sync"
)

// Task represents a unit of work.
type Task func(ctx context.Context) error

// Pool manages a pool of workers to execute tasks concurrently.
type Pool struct {
	taskQueue chan Task
	wg        sync.WaitGroup
	quit      chan struct{}
	maxWorker int
	ctx       context.Context
	cancel    context.CancelFunc
}

// NewPool creates a new worker pool.
func NewPool(maxWorker int) *Pool {
	ctx, cancel := context.WithCancel(context.Background())
	return &Pool{
		taskQueue: make(chan Task, maxWorker*2),
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

// Submit enqueues a task.
func (p *Pool) Submit(t Task) {
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
