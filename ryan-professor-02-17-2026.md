# Ryan and Professor Transcript

Date: 2026-02-17

Note: Cleaned for readability. Filler words were removed, and a few unclear spots are marked as `[unclear]`.

**Professor:** No one is going to let you recite the equation without presenting it. So that is a good practice. Okay, keep going.

**Ryan:** The rest of this is about plotting Euler and Runge-Kutta 4 relationships. For the error versus timestep size, this is going to be maximum error. These are some sample images from my code. I do not think we have to get into all of that.

The objective is to visualize and compare the Euler and fourth-order Runge-Kutta integration methods when applied to a projectile motion simulation, both with and without air resistance. The point is also to validate my code and show that it is accurate and correctly displays projectile motion.

So the main goal is to validate the accuracy of each integrator, both with and without air resistance, and to verify whether their observed error behavior matches theoretical expectations.

For the expected max error versus timestep relationships: because Euler is first order, that should mean its global truncation error scales with timestep. That means the error is proportional to the timestep size raised to the first power. So on a log-log plot comparing timestep to maximum error, the expectation is a slope of approximately 1.

The Runge-Kutta 4 method is a fourth-order integrator, so that means its global truncation error scales with timestep to the fourth power. On a log-log plot comparing timestep to max error, it should have a slope of 4.

For my method, I used two different cases. One is with no drag. In the no-drag case, I compared the RK4 and Euler solutions to the actual analytical closed form, because with no drag you can actually solve it analytically. With drag, I compared the Euler solution and the RK4 solution to a reference RK4 solution with a much smaller timestep.

For each integrator, position error was computed over time. Maximum position error was recorded. A timestep sweep was done over multiple timestep values, which helped me create a plot of maximum error versus timestep.

Here are the results.

In the trajectory comparison, in the no-drag case, Runge-Kutta 4 matches the analytical solution. You can see the RK4 and the analytical curve are completely the same.

**Professor:** I cannot see that.

**Ryan:**Should I zoom in?

**Professor:** No, in cases like this, either use points or crosses so the line goes through those markers. As it is, this is not easy to see. But it is very compelling. I assume your blue is under your green, right?

**Ryan:** Yes. The green completely covers it.

**Professor:** Very good.

**Professor:** And then Euler is that bad.

**Ryan:** Yes, it is pretty bad.

**Ryan:** When we add more timestep, Euler visibly gets farther away from the analytical solution.

**Professor:** And at times, if you increase the timestep. Right?

**Ryan:** Yes. When we increase the timestep size.

**Professor:** Why is that?

**Ryan:** Because the lower the timestep, the more accurate it is going to be. This is to show that with a higher timestep, Euler gets worse than RK4.

**Professor:** I want to sharpen the wording a little so you can express yourself clearly. Say "timestep size increases," not just "timestep increases." If you mention the number, people usually associate that with the number of timesteps. But the size of the timestep is what this is saying. I know you know this, but I want to be more precise.

**Ryan:** Right, timestep size increases. Delta t. Hold on. Very good. I am going to edit that after. It is not letting me change it.

So in this graph here, the timestep is 0.3, as opposed to this one where it is 0.1, meaning the timestep size, the change in time.

With air resistance, the Euler method slightly fails to match the Runge-Kutta 4 method, which is more accurate, and this is with a timestep size of 0.1.

As timestep size increases, Euler measurably deviates, but this time Runge-Kutta 4 also slightly deviates. You can see here it deviates from the original. The Runge-Kutta 4 method was originally here, but when we add timestep size, it gets a little less accurate.

**Professor:** What are these spots telling you?

**Ryan:** The same idea: with a larger timestep size, the graph is less precise. Because it is only being measured at this point, this point, this point, and this point, it is going to be less accurate than when it is measured at every smaller step.

**Professor:** You could express that more precisely by saying: from our simulation without air resistance, we established that Runge-Kutta is much more accurate than Euler. Therefore, now with air resistance, we trust the Runge-Kutta computations more.

You expect the same level of integration error to be present with or without air resistance, because you are doing similar numerical integration with the same two methods. The nice thing in the non-air-resistance case is that you can compare it to what you should have gotten exactly. That is why later you compare how the error, meaning the difference between the analytical and numerical solution, goes with Delta t. All right, keep going.

**Ryan:** Here is the position error versus time. The Euler method accumulates error roughly linearly in the no-drag case. We can see that the Runge-Kutta 4 method does not accumulate much error for this timestep.

**Professor:** Earlier, you said the log-log plot is going to have slope 1 and slope 4. So why are you showing me a linear-linear plot?

**Ryan:** Because this one is position error. I did not compare Runge-Kutta 4 to itself. This is position error instead of maximum error on a log-log plot. Over here we have the max error versus timestep, and we can see that with the RK4 method, the maximum error is nearly a slope of 4.

In the situation with drag, we can see that for Euler, the way it accumulates error with position is a little more curved. It is not linear like this one.

**Professor:** This kind of scaling does not really tell you anything meaningful about the blue line. That is why the linear scale does not work.

**Ryan:** Is the RK4 line basically at 0 because the values are so small that it does not visibly accumulate error?

**Professor:** Yes. I cannot see it on this plot. That is why it has to go on a log-log plot. Try that yourself. Make this a log-log plot and see what you get.

**Ryan:** Okay. For the maximum error versus timestep, the log-log plot shows that Euler exhibits approximately first-order convergence, and RK4 exhibits approximately fourth-order convergence.

**Professor:** Excellent. That is beautiful. Is it what you expected?

**Ryan:** Pretty much. It is exactly what I expected, except it is not exactly 4.

**Professor:** We will call that a victory.

**Ryan:** The reason it is not exactly 4 is that you cannot have a perfect reference solution where the timestep is zero. Also, there is air resistance and other factors like that.

The conclusion is that Euler is first-order accurate, RK4 is fourth-order accurate in my simulation, and my code accurately incorporates the integrators into a projectile motion simulation.

**Professor:** Very nice job. This is very mature work. I know we talked pretty fast last time, but you caught everything I wanted you to illustrate. That last plot was really your punch line, your money shot. Wonderful. I have plots like that in my papers showing convergence at a certain rate for different methods, and on a log-log plot it is a straight line. It really cannot paint the picture of parallel behavior any better than a straight line on a log-log plot.

**Ryan:** Thank you. When I coded this, I wanted to know why the log-log plot is linear. What I worked out is that the equation is error equals timestep raised to the order. Then when you take the log of both sides, the order becomes the slope.

**Professor:** That is exactly what we went over in class a couple weeks ago in my junior-level astrophysics class, showing the importance of log scales. You can present data that is hugely disparate. Look, for example, at the first orange and first blue points. They are off by eight or more orders of magnitude. If you were to plot both on a linear-linear plot, you would only see the orange plot and the blue would just be around zero.

**Ryan:** Right. You would not even be able to see it.

**Professor:** Exactly. You would just see it as a flat line around zero. That is why this is great. You really must use a log-log scale when your data is so disparate. Sometimes you can use log in one scale and linear in the other.

**Ryan:** Really?

**Professor:** Yes, but then you do not have the luxury of this power-law interpretation. This is great.

**Ryan:** Thank you. Is there any advice you have? Obviously you want me to make this log-log, and I actually want to see that. Is there anything else you think I could add to this, or do you think it is good as it is?

**Professor:** As a matter of fact, I do. I would like you to investigate an additional level of convincing your audience that you did this right, especially since you have the luxury of knowing the exact solution in this case.

Show that the numerical solution converges to the real solution as you decrease the step size, and do this on a log-log scale. On the x-axis, have the log of Delta t. On the y-axis, have a quantity we will call chi-squared for now. Chi is a Greek letter. Chi-squared is a goodness-of-fit measure: the sum of the squares of the differences between the exact and experimental values.

**Ryan:** Is that kind of like linear regression?

**Professor:** Yes, exactly. It is a measure of how good the fit is. Look up chi-squared. Technically, it involves the number of points and the sum of squared differences. When you get that, make chi-squared a function of timestep. Do a bunch of simulations with different timestep sizes, Delta t, and record chi-squared for each one.

That will show you a slope. It will also show that one method converges to the right solution faster than the other, because if you make the timestep small enough, even Euler will eventually agree visually with the exact solution. Runge-Kutta will do it much sooner, and you will see all of that come out in a plot of chi-squared versus Delta t on a log-log scale. Does that make sense?

**Ryan:** Yes, that makes perfect sense. I am going to look into that. Do you think I should let you know when I have that done, along with some of the other stuff you requested?

**Professor:** Yes, that would be good, if you would like. If these little chats help you, keep doing that. Whatever you need to get started, if you have any questions, I am happy to answer.

**Ryan:** Thank you so much. Next time we talk, do you think you could maybe give me some ideas for another project to work on? Maybe something more experimental. Not necessarily something completely open-ended, because I do not feel ready for that yet, but something more like an experiment where I am trying to figure something out.

**Professor:** How old are you?

**Ryan:** Around 15.

**Professor:** Fifteen. All right. We have a program for undergraduate students. If you were 18, I would attach you to our undergraduate cohort to do something like that. But you are too young, so we would have to do this independently. We have a nice undergraduate program at Jefferson Lab.

I think we also have a program for high school students. Look it up. Search for Jefferson Lab high school summer program.

**Ryan:** Okay.

**Professor:** Let me see if I can find more information on that.

Now I want to transition to something different. Let us see if this can be useful. Would you want to try doing research related to the kind of work I do?

**Ryan:** Sure.

**Professor:** All right. I just started reading. Go to my website. Have you been there?

**Ryan:** Yes. You work on accelerator physics, right?

**Professor:** Yes, and cosmology too, but we are going to get you started with accelerator physics. Go there and go to publications.

No, go to teaching and mentoring. The best way to start in a new field is with somebody's PhD work. Go to number 10 on the right column, Eric Johnson. Click on his dissertation. Then download it.

You can start reading from there, and if that is too dense, go back. He did an undergraduate senior thesis with me back in [unclear year], and then a PhD five years later. Start from there. The PhD thesis is this on steroids, obviously.

Read about ion sources, and maybe next time we can chat about what they are. Finish this up with the extra graph I asked you to make. Do the simulations, and then we can discuss what you think of the ion sources. Eventually I may be able to lead you toward running some simulations and doing some work. I do not know exactly where it will go, but eventually we can figure it out. You need to get acquainted with this idea of ion beam scattering.

**Ryan:** Okay, sounds good.

**Professor:** Prepare that for me next time. Whenever you are ready, just contact me and we will meet.

**Ryan:** Thank you. I wrote a lot of that down. I have a lot of it saved here. I am going to work on that. It was a very helpful meeting, and thank you for your advice.

**Professor:** I am glad this was helpful. You did a wonderful job. You should be proud of the effort you put in. This is the type of college-level effort I expect from my physics major students in college, so you should pat yourself on the back. I cannot wait to see what else you can do. This could lead to a research project, maybe even a paper before you graduate high school.

**Ryan:** Thank you.

**Professor:** Go back to my website. Go to publications now. Go down to 2018. Click on that paper. Zoom in some more. Look at the affiliation of the first author: Princess Anne High School. The student was 16 years old when he did work with me.

**Ryan:** Really?

**Professor:** Yes. He was 17 when it was eventually published, and he deserved first author. I did not give him anything. He earned it and did all that work. Really smart kid. He went on to Princeton and got straight A's there. Amazing student.

I firmly believe that if somebody is smart, age is not an impediment. He was published before he was 17. That is a rare thing. You cannot expect to see that often, even among high school students who want to become scientists. But why not do it twice?

**Ryan:** That sounds like something I would love to do.

**Professor:** Let us see. Very good. That is also in the same ion source context. You can read that paper. It is about the code we developed to simulate these things, but all of that will make more sense after you start reading. If you have questions, write them down, and then ask them next time we meet.

**Ryan:** Thank you so much. Have a good rest of your day.

**Professor:** You too. Nice chatting with you. If you have any questions, please feel free to reach out whenever.

**Ryan:** I will. Thank you.

**Professor:** All right. Bye.
